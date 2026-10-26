"""Finds out whether the remote repository is visible to everyone.

Two ways are tried. The API of the git host answers precisely (public, internal or private) when the
access token may read the repository. Without an answer from the API, an anonymous `git ls-remote`
tells whether anybody can clone it: if that works, the repository is public.
"""
import base64
import json
import ssl
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import quote, urlsplit

HOST_HINTS = (("github", "github"), ("gitlab", "gitlab"), ("bitbucket", "bitbucket"), ("codeberg", "forgejo"),
              ("forgejo", "forgejo"), ("gitea", "gitea"))


@dataclass
class Visibility:
    state: str            # public | private | unknown
    via: str = ""         # api | anonymous | none
    provider: str = ""
    detail: str = ""      # e.g. "internal", or the reason that nothing could be found out

    def as_dict(self):
        return {"state": self.state, "via": self.via, "provider": self.provider, "detail": self.detail}


def detect_provider(url, configured="auto"):
    if configured not in ("auto", "other"):
        return configured
    host = (urlsplit(url).hostname or "").lower()
    for hint, provider in HOST_HINTS:
        if hint in host:
            return provider
    return "other"


def repository_path(url):
    """owner/name from the URL path, without .git; nested groups (GitLab) stay whole."""
    path = urlsplit(url).path.strip("/")
    return path[:-4] if path.endswith(".git") else path


def _get_json(url, username, password, verify):
    headers = {"Accept": "application/json", "User-Agent": "home-assistant-git-exporter"}
    if password:
        token = base64.b64encode(f"{username or 'git'}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    context = None if verify else ssl._create_unverified_context()  # noqa: S323 - the user switched checking off
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=12, context=context) as reply:
        return json.load(reply)


def _api_url(provider, url):
    parts = urlsplit(url)
    base = f"{parts.scheme}://{parts.netloc}"
    path = repository_path(url)
    if provider == "github":
        if parts.hostname in ("github.com", "www.github.com"):
            return f"https://api.github.com/repos/{path}"
        return f"{base}/api/v3/repos/{path}"
    if provider == "gitlab":
        return f"{base}/api/v4/projects/{quote(path, safe='')}"
    if provider in ("gitea", "forgejo"):
        return f"{base}/api/v1/repos/{path}"
    if provider == "bitbucket":
        return f"https://api.bitbucket.org/2.0/repositories/{path}"
    return None


def _from_api(provider, body):
    """public, private or None from a host's answer."""
    if provider == "gitlab":
        return {"public": "public", "internal": "private", "private": "private"}.get(body.get("visibility"))
    if provider == "bitbucket":
        return "private" if body.get("is_private") else "public" if body.get("is_private") is False else None
    if isinstance(body.get("private"), bool):
        return "private" if body["private"] else "public"
    return None


def check(repository):
    """The Visibility of a gitops.Repository's remote."""
    provider = detect_provider(repository.url, repository.config.provider)
    endpoint = _api_url(provider, repository.url)
    detail = ""
    if endpoint:
        try:
            body = _get_json(endpoint, repository.username, repository.password, repository.config.ssl_verification)
            state = _from_api(provider, body)
            if state:
                extra = body.get("visibility") if provider == "gitlab" else ""
                return Visibility(state, "api", provider, extra or "")
            detail = "unexpected answer from the API"
        except urllib.error.HTTPError as error:
            detail = f"the API answered HTTP {error.code}"
        except (urllib.error.URLError, OSError, ValueError, ssl.SSLError) as error:
            detail = f"the API is not reachable ({error})"
    try:
        readable = repository.readable_without_login()
    except (subprocess.TimeoutExpired, OSError):
        readable = None
    if readable is True:
        return Visibility("public", "anonymous", provider, "anyone can clone it")
    if readable is False:
        return Visibility("private", "anonymous", provider, "it asks for a login")
    return Visibility("unknown", "none", provider, detail or "the remote could not be reached")


def decision(repository_config, found, acknowledged):
    """What to do about a visibility check.

    Returns (action, reason): action is "go", "hold" or "note".
      private audience on a public remote -> hold, unless the user allowed it
      unknown visibility for a private audience -> note (the user is told, the export goes on)
    """
    if repository_config.public:
        return "go", ""
    if found.state == "public" and not (repository_config.allow_public_remote or acknowledged):
        return "hold", "public_remote"
    if found.state == "unknown":
        return "note", "unknown"
    return "go", ""

