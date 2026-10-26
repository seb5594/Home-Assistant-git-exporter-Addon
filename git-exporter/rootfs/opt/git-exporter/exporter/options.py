"""The app options as the exporter uses them.

The Supervisor stores the options and writes them to /data/options.json when the app starts. Changes
made later, in the web interface of this app or on the configuration page, are only known to the
Supervisor, so the current options are asked from there and the file is the fallback.

Version 1 had one `repository` and a `dry_run` switch. Those options still validate; an old
`repository` becomes the first entry of `repositories` (see migrate).
"""
import copy
import json
import os
import re
from dataclasses import dataclass, field

OPTIONS_FILE = os.environ.get("OPTIONS_FILE", "/data/options.json")

EXPORT_DEFAULTS = {
    "lovelace": True, "addons": True, "addon_configs": True, "esphome": True, "node_red": True, "local_apps": False,
}
CHECK_DEFAULTS = {"enabled": True, "check_for_secrets": True, "check_for_ips": True, "on_finding": "censor"}
BEHAVIOR_DEFAULTS = {"export_on_start": True, "stop_after_minutes": 10, "keep_running": False}
MAX_FILE_SIZE_MB = 5
AUDIENCES = ("public", "private")
PROVIDERS = ("auto", "github", "gitlab", "gitea", "forgejo", "bitbucket", "other")
DEFAULT_COMMIT_MESSAGE = "Home Assistant Git Exporter {DATE}"
# Options that the web interface may change; everything else is configuration in the strict sense.
EDITABLE = ("exclude", "presets", "export", "allowed_secrets", "secrets", "check", "limits", "behavior")


@dataclass
class Repository:
    name: str
    url: str
    slug: str = ""
    username: str = ""
    password: str = ""
    email: str = ""
    branch: str = "main"
    audience: str = "public"
    provider: str = "auto"
    commit_message: str = DEFAULT_COMMIT_MESSAGE
    pull_before_push: bool = True
    ssl_verification: bool = True
    check_visibility: bool = True
    allow_public_remote: bool = False
    enabled: bool = True

    @property
    def public(self):
        return self.audience == "public"


@dataclass
class Settings:
    repositories: list = field(default_factory=list)
    export: dict = field(default_factory=lambda: dict(EXPORT_DEFAULTS))
    presets: dict = field(default_factory=dict)
    exclude: list = field(default_factory=list)
    secrets: list = field(default_factory=list)
    allowed_secrets: list = field(default_factory=list)
    check: dict = field(default_factory=lambda: dict(CHECK_DEFAULTS))
    max_file_size_mb: int = MAX_FILE_SIZE_MB
    behavior: dict = field(default_factory=lambda: dict(BEHAVIOR_DEFAULTS))
    legacy_repository: bool = False

    @property
    def max_file_size(self):
        return self.max_file_size_mb * 1024 * 1024

    def draft(self, changes):
        """A copy with the editable parts replaced, for looking at the effect before saving."""
        copy_ = copy.deepcopy(self)
        for key in ("exclude", "secrets", "allowed_secrets"):
            if key in changes:
                setattr(copy_, key, _strings(changes[key]))
        for key in ("presets", "export", "check", "behavior"):
            if isinstance(changes.get(key), dict):
                getattr(copy_, key).update(changes[key])
        limits = changes.get("limits")
        if isinstance(limits, dict) and isinstance(limits.get("max_file_size_mb"), int):
            copy_.max_file_size_mb = max(1, limits["max_file_size_mb"])
        return copy_


def _strings(values):
    return [str(item).strip() for item in (values or []) if str(item).strip()]


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "repository"


def _boolean(value, default):
    return default if value is None else bool(value)


def _repository(entry, index):
    name = str(entry.get("name") or f"repository-{index + 1}").strip()
    audience = entry.get("audience")
    provider = entry.get("provider")
    return Repository(
        name=name,
        url=str(entry.get("url") or "").strip(),
        username=str(entry.get("username") or ""),
        password=str(entry.get("password") or ""),
        email=str(entry.get("email") or ""),
        branch=str(entry.get("branch") or entry.get("branch_name") or "main"),
        # An entry that does not say who it is for is treated as public: that is the careful reading.
        audience=audience if audience in AUDIENCES else "public",
        provider=provider if provider in PROVIDERS else "auto",
        commit_message=str(entry.get("commit_message") or DEFAULT_COMMIT_MESSAGE),
        pull_before_push=_boolean(entry.get("pull_before_push"), True),
        ssl_verification=_boolean(entry.get("ssl_verification"), True),
        check_visibility=_boolean(entry.get("check_visibility"), True),
        allow_public_remote=_boolean(entry.get("allow_public_remote"), False),
        enabled=_boolean(entry.get("enabled"), True),
    )


def parse(options):
    """Settings from the options dictionary of the Supervisor (or /data/options.json)."""
    options = options or {}
    settings = Settings()
    repositories = [_repository(entry, i) for i, entry in enumerate(options.get("repositories") or [])
                    if isinstance(entry, dict)]

    legacy = options.get("repository") or {}
    if legacy.get("url") and not any(r.url == legacy["url"] for r in repositories):
        # The single repository of version 1 was always exported with the secrets blanked: public.
        repositories.insert(0, _repository({**legacy, "name": "default", "audience": "public"}, 0))
        settings.legacy_repository = True

    used = set()
    for repository in repositories:
        base = slugify(repository.name)
        slug, number = base, 2
        while slug in used:
            slug, number = f"{base}-{number}", number + 1
        used.add(slug)
        repository.slug = slug
    settings.repositories = repositories

    settings.export = {**EXPORT_DEFAULTS, **{k: bool(v) for k, v in (options.get("export") or {}).items() if v is not None}}
    settings.presets = {k: bool(v) for k, v in (options.get("presets") or {}).items() if v is not None}
    settings.exclude = _strings(options.get("exclude"))
    settings.secrets = _strings(options.get("secrets"))
    settings.allowed_secrets = _strings(options.get("allowed_secrets"))
    settings.check = {**CHECK_DEFAULTS, **{k: v for k, v in (options.get("check") or {}).items() if v is not None}}
    if settings.check["on_finding"] not in ("censor", "block"):
        settings.check["on_finding"] = "censor"
    limits = options.get("limits") or {}
    if isinstance(limits.get("max_file_size_mb"), int) and limits["max_file_size_mb"] > 0:
        settings.max_file_size_mb = limits["max_file_size_mb"]
    settings.behavior = {**BEHAVIOR_DEFAULTS, **{k: v for k, v in (options.get("behavior") or {}).items() if v is not None}}
    return settings


def load_file():
    try:
        with open(OPTIONS_FILE, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def migrated_options(options, settings):
    """The options to store once a version 1 `repository` has become an entry of `repositories`.

    None when there is nothing to migrate. The password stays where it is, only moved.
    """
    legacy = (options or {}).get("repository") or {}
    if not settings.legacy_repository or not legacy.get("url"):
        return None
    updated = copy.deepcopy(options)
    entry = {"name": "default", "audience": "public"}
    for source, target in (("url", "url"), ("username", "username"), ("password", "password"), ("email", "email"),
                           ("branch_name", "branch"), ("commit_message", "commit_message"),
                           ("pull_before_push", "pull_before_push"), ("ssl_verification", "ssl_verification")):
        if legacy.get(source) not in (None, ""):
            entry[target] = legacy[source]
    updated["repositories"] = [entry] + [r for r in updated.get("repositories") or []]
    updated["repository"] = {}
    updated.pop("dry_run", None)
    return updated
