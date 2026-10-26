"""git on the command line, for one repository.

The credentials travel in an `Authorization` header that is handed to git through the environment.
They are not part of the remote URL, so they are neither written to .git/config nor shown in a
process list or an error message.
"""
import base64
import os
import subprocess
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
TIMEOUT = 300


class GitError(Exception):
    pass


def split_url(url, username="", password=""):
    """(url without credentials, username, password); credentials typed into the URL are used when none are given."""
    parts = urlsplit(url.strip())
    if parts.username and not username:
        username = parts.username
    if parts.password and not password:
        password = parts.password
    host = parts.hostname or ""
    if ":" in host:
        host = f"[{host}]"
    netloc = host + (f":{parts.port}" if parts.port else "")
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, "")), username, password


class Repository:
    """A local clone and the remote it belongs to."""

    def __init__(self, settings_repository, directory=None):
        self.config = settings_repository
        self.url, self.username, self.password = split_url(
            settings_repository.url, settings_repository.username, settings_repository.password)
        self.directory = Path(directory) if directory else DATA_DIR / "repositories" / settings_repository.slug

    # -- plumbing ------------------------------------------------------------------------------

    def _environment(self, authenticated=True):
        environment = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C", "GIT_ASKPASS": "/bin/true"}
        entries = []
        if not self.config.ssl_verification:
            entries.append(("http.sslVerify", "false"))
        if authenticated and self.password:
            token = base64.b64encode(f"{self.username or 'git'}:{self.password}".encode()).decode()
            entries.append(("http.extraHeader", f"Authorization: Basic {token}"))
        environment["GIT_CONFIG_COUNT"] = str(len(entries))
        for index, (key, value) in enumerate(entries):
            environment[f"GIT_CONFIG_KEY_{index}"] = key
            environment[f"GIT_CONFIG_VALUE_{index}"] = value
        return environment

    def _mask(self, text):
        for secret in filter(None, (self.password, quote(self.password, safe=""),
                                    base64.b64encode(f"{self.username or 'git'}:{self.password}".encode()).decode()
                                    if self.password else "")):
            text = text.replace(secret, "***")
        return text

    def git(self, *args, check=True, authenticated=True, cwd=None, timeout=TIMEOUT):
        try:
            done = subprocess.run(
                ["git", *args], cwd=cwd or self.directory, env=self._environment(authenticated),
                capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as error:
            raise GitError(f"git {args[0]} took longer than {timeout} seconds") from error
        if check and done.returncode != 0:
            detail = self._mask((done.stderr or done.stdout).strip())
            raise GitError(f"git {args[0]} failed: {detail}")
        return done

    # -- the clone -----------------------------------------------------------------------------

    def prepare(self):
        """Clone, or bring an existing clone up to date, and check out the branch."""
        config = self.config
        self.directory.mkdir(parents=True, exist_ok=True)
        if not (self.directory / ".git").exists():
            if any(self.directory.iterdir()):
                self.git("init", "-q")
                self.git("remote", "add", "origin", self.url)
            else:
                self.git("clone", "-q", self.url, str(self.directory), cwd=self.directory.parent)
        self.git("remote", "set-url", "origin", self.url)
        self.git("config", "user.name", self.username or "Home Assistant Git Exporter")
        self.git("config", "user.email", config.email or "git.exporter@home-assistant")
        self.git("config", "core.fileMode", "true")
        self.git("fetch", "-q", "origin")
        remote_branch = f"origin/{config.branch}"
        has_remote_branch = self.git("rev-parse", "--verify", "-q", remote_branch, check=False).returncode == 0
        if has_remote_branch and config.pull_before_push:
            # The working copy only holds what this app wrote, so the remote state is the starting point.
            self.git("checkout", "-q", "-f", "-B", config.branch, remote_branch)
        else:
            current = self.git("rev-parse", "--abbrev-ref", "HEAD", check=False).stdout.strip()
            if current != config.branch:
                exists = self.git("rev-parse", "--verify", "-q", config.branch, check=False).returncode == 0
                self.git("checkout", "-q", "-f", config.branch) if exists else self.git("checkout", "-q", "-B", config.branch)

    def tracked_files(self):
        done = self.git("ls-files", "-z", check=False)
        return [name for name in done.stdout.split("\0") if name]

    def status(self):
        """(code, path) pairs of `git status --porcelain`, for the files that differ from the last commit."""
        done = self.git("status", "--porcelain=v1", "-z", "--untracked-files=all", check=False)
        changes, entries = [], done.stdout.split("\0")
        index = 0
        while index < len(entries):
            entry = entries[index]
            index += 1
            if len(entry) < 4:
                continue
            code, path = entry[:2], entry[3:]
            if code[0] in "RC":
                index += 1  # the original name of a rename follows as its own entry
            changes.append((code.strip() or "?", path))
        return changes

    def commit_all(self, message):
        """Stages everything and commits. Returns False when there was nothing to commit."""
        self.git("add", "-A")
        if self.git("diff", "--cached", "--quiet", check=False).returncode == 0:
            return False
        self.git("commit", "-q", "-m", message)
        return True

    def has_unpushed_commits(self):
        remote_branch = f"origin/{self.config.branch}"
        if self.git("rev-parse", "--verify", "-q", remote_branch, check=False).returncode != 0:
            return self.git("rev-parse", "--verify", "-q", "HEAD", check=False).returncode == 0
        done = self.git("rev-list", "--count", f"{remote_branch}..HEAD", check=False)
        return done.stdout.strip() not in ("", "0")

    def push(self):
        self.git("push", "-q", "origin", f"HEAD:refs/heads/{self.config.branch}")

    def head_content(self, path):
        """A file as it is in the last commit; None when it is not there."""
        done = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=self.directory, env=self._environment(False),
                              capture_output=True, check=False)
        return done.stdout if done.returncode == 0 else None

    # -- the remote ----------------------------------------------------------------------------

    def readable_without_login(self):
        """True when anyone can clone the remote, False when it asks for a login, None when it cannot be reached."""
        done = subprocess.run(
            ["git", "-c", "credential.helper=", "ls-remote", "--heads", self.url], env=self._environment(False),
            capture_output=True, text=True, timeout=45, check=False)
        if done.returncode == 0:
            return True
        message = (done.stderr or "").lower()
        if any(word in message for word in ("authentication", "terminal prompts disabled", "not found", "403", "401",
                                              "could not read username", "invalid credentials", "repository not found")):
            return False
        return None
