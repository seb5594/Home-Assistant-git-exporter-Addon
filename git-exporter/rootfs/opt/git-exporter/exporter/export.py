"""Builds what goes into a repository, compares it with what is there, and writes it.

`collect` turns the sources into Outputs: for each file in the repository its content, already
censored when the repository is public. `plan` compares them with the working copy; `apply`
writes the difference. A preview is a plan that is never applied, so what it shows is exactly what
an export would do.
"""
import difflib
import filecmp
import json
import os
import shutil
import time
from collections import Counter
from dataclasses import dataclass, field

import yaml

from . import sanitize, sources, supervisor

YAML_SUFFIXES = (".yaml", ".yml")
TEXT_SUFFIXES = (
    ".yaml", ".yml", ".json", ".js", ".py", ".md", ".txt", ".conf", ".cfg", ".ini", ".toml", ".sh", ".jinja", ".j2",
    ".html", ".css", ".xml", ".csv", ".lua", ".jsonl", ".disabled", ".properties", ".service", ".rules",
)
SNIFF_LIMIT = 256 * 1024
CENSOR_LIMIT = 5 * 1024 * 1024
DIFF_LINES = 400
# Folders the exporter owns in a repository. Everything else in the repository is left alone.
MANAGED = ("config", "esphome", "node-red", "local_apps", "addons_config", "lovelace", "addons")


@dataclass
class Output:
    path: str                    # path in the repository
    size: int
    file: str | None = None      # copy this file ...
    data: bytes | None = None    # ... or write these bytes
    executable: bool = False
    censored: int = 0


@dataclass
class Collected:
    outputs: dict = field(default_factory=dict)
    findings: Counter = field(default_factory=Counter)
    findings_by_file: dict = field(default_factory=dict)
    blocked: dict = field(default_factory=dict)       # path -> reason: not exported at all
    warnings: list = field(default_factory=list)      # (code, args)
    synced: set = field(default_factory=set)          # top-level folders that were built this time
    too_large: int = 0
    secrets_error: str | None = None


@dataclass
class Change:
    path: str
    status: str                  # added | modified | removed
    size: int = 0
    old_size: int = 0
    censored: int = 0


@dataclass
class Plan:
    changes: list = field(default_factory=list)
    unchanged: int = 0
    collected: Collected = field(default_factory=Collected)

    def counts(self):
        count = Counter(change.status for change in self.changes)
        return {"added": count["added"], "modified": count["modified"], "removed": count["removed"],
                "unchanged": self.unchanged}


def _is_text_candidate(path, size):
    if path.lower().endswith(TEXT_SUFFIXES):
        return size <= CENSOR_LIMIT
    return size <= SNIFF_LIMIT and "." not in os.path.basename(path)


def _is_yaml(path):
    return path.lower().endswith(YAML_SUFFIXES)


def _make_censor(settings, secrets_text, collected):
    secrets, error = ([], None)
    if secrets_text:
        secrets, error = sanitize.parse_secrets(secrets_text)
        if error:
            collected.secrets_error = error
            collected.warnings.append(("secrets_unreadable", {"error": error}))
    check = settings.check
    return sanitize.Censor(
        secrets, settings.secrets, settings.allowed_secrets,
        check_secrets=check["enabled"] and check["check_for_secrets"],
        check_addresses=check["enabled"] and check["check_for_ips"])


def _read_secrets(settings):
    root = sources.BY_ID["config"].root()
    path = os.path.join(root, sources.SECRETS_FILE) if root else None
    if path and os.path.isfile(path):
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                return handle.read()
        except OSError:
            return ""
    return ""


def _record(collected, path, result):
    if result.findings:
        collected.findings.update(result.findings)
        collected.findings_by_file[path] = dict(result.findings)


def _add_text(collected, path, text, censor, public, yaml_file, executable=False):
    """Adds a generated or read text; in a public repository it is censored first."""
    censored = 0
    if public:
        result = censor.apply(text, path, yaml_file)
        if result.blocked:
            collected.blocked[path] = result.blocked
            return
        _record(collected, path, result)
        text, censored = result.text, sum(result.findings.values())
    data = text.encode("utf-8")
    collected.outputs[path] = Output(path, len(data), data=data, executable=executable, censored=censored)


def _collect_tree(collected, source, settings, censor, public):
    rules = sources.Rules(source, settings)
    root = source.root()
    for item in sources.walk(rules, include_excluded=True):
        if item.is_dir:
            continue
        if item.decision.status == "too_large":
            collected.too_large += 1
            continue
        if item.decision.excluded:
            continue
        path = f"{source.dest}/{item.path}"
        absolute = os.path.join(root, item.path)
        executable = item.path.endswith(".sh")
        if item.path == sources.SECRETS_FILE and source.id in ("config", "esphome"):
            _add_secrets_file(collected, path, absolute, public)
        elif public and _is_text_candidate(item.path, item.size):
            try:
                with open(absolute, "rb") as handle:
                    raw = handle.read()
            except OSError:
                continue
            if sanitize.looks_like_text(raw):
                _add_text(collected, path, raw.decode("utf-8"), censor, public, _is_yaml(item.path), executable)
                continue
            collected.outputs[path] = Output(path, item.size, file=absolute, executable=executable)
        else:
            collected.outputs[path] = Output(path, item.size, file=absolute, executable=executable)
    collected.synced.add(source.dest)


def _add_secrets_file(collected, path, absolute, public):
    try:
        with open(absolute, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return
    if public:
        text = sanitize.blank_secrets_yaml(text)
    data = text.encode("utf-8")
    collected.outputs[path] = Output(path, len(data), data=data)


def _collect_lovelace(collected, censor, public):
    root = sources.BY_ID["config"].root()
    folder = os.path.join(root, ".storage") if root else None
    if not folder or not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.startswith("lovelace"):
            continue
        try:
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                content = json.load(handle).get("data")
        except (OSError, ValueError, AttributeError):
            collected.warnings.append(("lovelace_unreadable", {"name": name}))
            continue
        text = yaml.dump(content, default_flow_style=False)
        _add_text(collected, f"lovelace/{name}.yaml", text, censor, public, True)
    collected.synced.add("lovelace")


def _collect_apps(collected, censor, public):
    if not supervisor.available():
        collected.warnings.append(("supervisor_missing", {}))
        return
    try:
        slugs = supervisor.installed_apps()
        for slug in slugs:
            options = (supervisor.app_info(slug) or {}).get("options") or {}
            _add_text(collected, f"addons/{slug}.yaml", yaml.dump(options, default_flow_style=False), censor, public, True)
        repositories = [entry for entry in supervisor.store_repositories()
                        if entry.get("source") not in (None, "core", "local")]
        listing = {entry["name"]: {k: entry.get(k) for k in ("source", "maintainer", "slug")} for entry in repositories}
        _add_text(collected, "addons/repositories.yaml", yaml.dump(listing, default_flow_style=False),
                  censor, public, True)
        collected.synced.add("addons")
    except supervisor.SupervisorError as error:
        collected.warnings.append(("apps_unavailable", {"error": str(error)}))


def collect(settings, repository, progress=None):
    """Everything that belongs into the repository, as it would be written."""
    collected = Collected()
    public = repository.public
    censor = _make_censor(settings, _read_secrets(settings) if public else "", collected)
    active = sources.active(settings)
    for source in active:
        if progress:
            progress(source.id)
        _collect_tree(collected, source, settings, censor, public)
    if settings.export.get("lovelace"):
        if progress:
            progress("lovelace")
        _collect_lovelace(collected, censor, public)
    if settings.export.get("addons"):
        if progress:
            progress("addons")
        _collect_apps(collected, censor, public)
    return collected


# ---- comparing and writing --------------------------------------------------------------------


def _same(output, current):
    if output.data is not None:
        try:
            with open(current, "rb") as handle:
                return handle.read() == output.data
        except OSError:
            return False
    try:
        return os.path.getsize(current) == output.size and filecmp.cmp(output.file, current, shallow=False)
    except OSError:
        return False


def _existing(directory, synced):
    """Files in the working copy below the folders that were built, as {path: size}."""
    found = {}
    for top in synced:
        base = os.path.join(directory, top)
        for folder, names, files in os.walk(base):
            names[:] = [name for name in names if name != ".git"]
            for name in files:
                full = os.path.join(folder, name)
                found[os.path.relpath(full, directory).replace(os.sep, "/")] = os.path.getsize(full)
    return found


def plan(collected, directory):
    """What writing `collected` into the working copy at `directory` would change."""
    result = Plan(collected=collected)
    existing = _existing(directory, collected.synced)
    for path, output in sorted(collected.outputs.items()):
        if not any(path == top or path.startswith(top + "/") for top in collected.synced):
            continue
        current = os.path.join(directory, path)
        if path not in existing:
            result.changes.append(Change(path, "added", output.size, 0, output.censored))
        elif _same(output, current):
            result.unchanged += 1
        else:
            result.changes.append(Change(path, "modified", output.size, existing[path], output.censored))
    for path, size in sorted(existing.items()):
        if path not in collected.outputs:
            result.changes.append(Change(path, "removed", 0, size))
    return result


def apply(plan_, directory):
    """Writes the plan into the working copy."""
    outputs = plan_.collected.outputs
    for change in plan_.changes:
        target = os.path.join(directory, change.path)
        if change.status == "removed":
            try:
                os.remove(target)
            except FileNotFoundError:
                pass
            continue
        output = outputs[change.path]
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if output.data is not None:
            with open(target, "wb") as handle:
                handle.write(output.data)
        else:
            shutil.copyfile(output.file, target)
        os.chmod(target, 0o755 if output.executable else 0o644)
    for top in plan_.collected.synced:
        _prune_empty(os.path.join(directory, top))


def _prune_empty(base):
    for folder, _names, _files in os.walk(base, topdown=False):
        if folder != base and not os.listdir(folder):
            os.rmdir(folder)


# ---- diffs for the web interface --------------------------------------------------------------


def diff(plan_, directory, path, mask=()):
    """A unified diff of one change, with the given secret values hidden. None for binary content."""
    output = plan_.collected.outputs.get(path)
    current = os.path.join(directory, path)
    old = new = b""
    if os.path.isfile(current):
        with open(current, "rb") as handle:
            old = handle.read(CENSOR_LIMIT)
    if output is not None:
        if output.data is not None:
            new = output.data
        else:
            with open(output.file, "rb") as handle:
                new = handle.read(CENSOR_LIMIT)
    if not (sanitize.looks_like_text(old) and sanitize.looks_like_text(new)):
        return None
    lines = list(difflib.unified_diff(old.decode().splitlines(), new.decode().splitlines(), "before", "after",
                                      lineterm="", n=2))
    text = "\n".join(lines[:DIFF_LINES]) + ("\n…" if len(lines) > DIFF_LINES else "")
    for value in sorted(mask, key=len, reverse=True):
        text = text.replace(value, "••••")
    return text


def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")
