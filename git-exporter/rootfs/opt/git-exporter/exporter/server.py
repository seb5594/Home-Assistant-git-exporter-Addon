"""The web interface behind Home Assistant's ingress, and the JSON API it talks to.

Only Home Assistant's ingress proxy and the container itself may call it (the proxy has already
checked who is asking). Nothing here returns a password.
"""
import json
import mimetypes
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from . import export, gitops, log, matcher, options, presets, runner, sources, state, supervisor, visibility

WEB_DIR = Path(os.environ.get("WEB_DIR", "/opt/git-exporter/web"))
ALLOWED_ADDRESSES = {"172.30.32.2", "::ffff:172.30.32.2", "127.0.0.1", "::ffff:127.0.0.1", "::1"}
MAX_BODY = 1024 * 1024
LISTING_LIMIT = 4000
CHANGE_LIMIT = 6000


class ApiError(Exception):
    def __init__(self, code, message="", status=400):
        super().__init__(message or code)
        self.code, self.status = code, status


class Job:
    def __init__(self, kind, target):
        self.id = uuid.uuid4().hex[:12]
        self.kind, self.target = kind, target
        self.stage, self.done = "queued", False
        self.results, self.plans = [], {}
        self.started = time.time()


class Application:
    """The state the web interface works on."""

    def __init__(self, load_settings, version):
        self.load_settings = load_settings
        self.version = version
        self.jobs = {}
        self.job_lock = threading.Lock()
        self.last_activity = time.monotonic()
        self.auto_result = None
        self.keep_running = None     # set from the web interface; None follows the options

    # -- settings ------------------------------------------------------------------------------

    def settings(self, draft=None):
        current = self.load_settings()
        return current.draft(draft) if draft else current

    def find(self, settings, name):
        for repository in settings.repositories:
            if name in (repository.slug, repository.name):
                return repository
        raise ApiError("unknown_repository", name, 404)

    # -- views ---------------------------------------------------------------------------------

    def repository_view(self, repository):
        remembered = state.get(repository.slug)
        url, _user, _password = gitops.split_url(repository.url, repository.username, repository.password)
        return {
            "name": repository.name, "slug": repository.slug, "url": url, "branch": repository.branch,
            "audience": repository.audience, "provider": visibility.detect_provider(repository.url, repository.provider),
            "enabled": repository.enabled, "check_visibility": repository.check_visibility,
            "allow_public_remote": repository.allow_public_remote,
            "accepted_public_remote": state.public_remote_accepted(repository.slug, url),
            "last_run": remembered.get("last_run"), "has_login": bool(repository.password),
        }

    def preset_view(self, settings):
        return [{"id": p.id, "patterns": list(p.patterns), "title": p.title, "description": p.description,
                 "enabled": presets.enabled(p, settings.presets), "default": p.default,
                 "sources": list(p.sources) if p.sources else None} for p in presets.PRESETS]

    def source_view(self, settings):
        found = []
        for source in sources.SOURCES:
            root = source.root()
            switched_on = not source.export_flag or settings.export.get(source.export_flag)
            found.append({"id": source.id, "title": source.title, "dest": source.dest, "root": root,
                          "available": bool(root), "enabled": bool(switched_on)})
        return found

    def state_view(self):
        settings = self.settings()
        return {
            "version": self.version, "supervisor": supervisor.available(),
            "repositories": [self.repository_view(r) for r in settings.repositories],
            "sources": self.source_view(settings), "presets": self.preset_view(settings),
            "exclude": settings.exclude, "allowed_secrets": settings.allowed_secrets, "secrets": settings.secrets,
            "export": settings.export, "check": settings.check, "behavior": settings.behavior,
            "limits": {"max_file_size_mb": settings.max_file_size_mb},
            "auto_result": self.auto_result, "legacy_repository": settings.legacy_repository,
            "idle_seconds": int(time.monotonic() - self.last_activity),
            "keep_running": settings.behavior["keep_running"] if self.keep_running is None else self.keep_running,
            "busy": any(not job.done for job in self.jobs.values()),
            "mounts": {kind: [c for c in candidates if os.path.isdir(c)] for kind, candidates in sources.ROOTS.items()},
        }

    # -- the file tree -------------------------------------------------------------------------

    def tree(self, body):
        settings = self.settings(body.get("draft"))
        source = sources.BY_ID.get(body.get("source"))
        if source is None or source.root() is None:
            raise ApiError("unknown_source", status=404)
        rel = str(body.get("path") or "").strip("/")
        if ".." in rel.split("/"):
            raise ApiError("bad_path")
        rules = sources.Rules(source, settings)
        items = sources.list_dir(rules, rel)
        items.sort(key=lambda item: (not item.is_dir, item.path.lower()))
        return {"path": rel, "truncated": len(items) > LISTING_LIMIT,
                "entries": [{"path": i.path, "name": i.path.rsplit("/", 1)[-1], "dir": i.is_dir, "size": i.size,
                             "status": i.decision.status, "rule": i.decision.rule, "origin": i.decision.origin}
                            for i in items[:LISTING_LIMIT]]}

    def summary(self, body):
        settings = self.settings(body.get("draft"))
        source = sources.BY_ID.get(body.get("source"))
        if source is None or source.root() is None:
            raise ApiError("unknown_source", status=404)
        return sources.summarize(sources.Rules(source, settings))

    def pattern_effect(self, body):
        """Which files an extra pattern would add to the excluded ones, and which it would bring back."""
        pattern = str(body.get("pattern") or "").strip()
        problem = matcher.check(pattern)
        if problem:
            raise ApiError("bad_pattern", problem)
        base = self.settings(body.get("draft"))
        extended = base.draft({"exclude": base.exclude + [pattern]})
        deadline = time.monotonic() + 20
        affected, files, size, complete = [], 0, 0, True
        for source in sources.active(base):
            before, after = sources.Rules(source, base), sources.Rules(source, extended)
            root = source.root()
            stack = [("", sources.INCLUDED, sources.INCLUDED)]
            while stack and complete:
                rel, state_before, state_after = stack.pop()
                try:
                    entries = sorted(os.scandir(os.path.join(root, rel) if rel else root), key=lambda e: e.name)
                except OSError:
                    continue
                for entry in entries:
                    if entry.is_symlink():
                        continue
                    is_dir = entry.is_dir(follow_symlinks=False)
                    path = f"{rel}/{entry.name}" if rel else entry.name
                    size_now = 0 if is_dir else entry.stat(follow_symlinks=False).st_size
                    one = before.decide(path, is_dir, size_now, state_before)
                    two = after.decide(path, is_dir, size_now, state_after)
                    if is_dir:
                        stack.append((path, one, two))
                    elif one.excluded != two.excluded:
                        files += 1
                        size += size_now
                        if len(affected) < 40:
                            affected.append({"source": source.id, "path": path, "now_excluded": two.excluded, "size": size_now})
                if time.monotonic() > deadline:
                    complete = False
        return {"pattern": pattern, "files": files, "bytes": size, "examples": affected, "complete": complete}

    # -- jobs ----------------------------------------------------------------------------------

    def start_job(self, kind, repositories, **flags):
        if any(not job.done for job in self.jobs.values()):
            raise ApiError("busy", "Another run is still going.", 409)
        job = Job(kind, [r.slug for r in repositories])
        self.jobs[job.id] = job
        for old in sorted(self.jobs.values(), key=lambda j: j.started)[:-6]:
            self.jobs.pop(old.id, None)
        threading.Thread(target=self._run_job, args=(job, repositories, flags), daemon=True).start()
        return job

    def _run_job(self, job, repositories, flags):
        settings = flags.pop("settings")
        dry_run = job.kind == "preview"
        try:
            for repository in repositories:
                job.stage = f"{repository.name}"
                result, plan = runner.run(settings, repository, dry_run=dry_run,
                                          progress=lambda stage, r=repository: setattr(job, "stage", f"{r.name}:{stage}"),
                                          **flags)
                if not dry_run:
                    runner.remember_result(result)
                    level = log.info if result["status"] == runner.STATUS_OK else log.warning
                    level(f"{repository.name}: {runner.describe(result)}")
                job.results.append(result)
                if plan is not None:
                    job.plans[repository.slug] = (plan, str(gitops.Repository(repository).directory))
        except Exception as problem:  # noqa: BLE001 - the job must always finish
            log.error(f"The run failed: {problem}")
            job.results.append({"repository": "", "status": "error", "code": "error", "args": {"message": str(problem)}})
        job.done = True

    def job_view(self, job_id):
        job = self.jobs.get(job_id)
        if job is None:
            raise ApiError("unknown_job", status=404)
        results = []
        for result in job.results:
            entry = dict(result)
            held = job.plans.get(result.get("slug"))
            if held:
                changes = held[0].changes
                entry["changes"] = [{"path": c.path, "status": c.status, "size": c.size, "old_size": c.old_size,
                                     "censored": c.censored} for c in changes[:CHANGE_LIMIT]]
                entry["changes_truncated"] = len(changes) > CHANGE_LIMIT
                entry["findings_by_file"] = dict(list(held[0].collected.findings_by_file.items())[:200])
            results.append(entry)
        return {"id": job.id, "kind": job.kind, "stage": job.stage, "done": job.done, "results": results}

    def diff(self, job_id, slug, path):
        job = self.jobs.get(job_id)
        held = job.plans.get(slug) if job else None
        if not held:
            raise ApiError("unknown_job", status=404)
        plan, directory = held
        settings = self.settings()
        text = export.diff(plan, directory, path, mask=runner._secret_values(settings))
        return {"path": path, "diff": text, "binary": text is None}

    # -- saving --------------------------------------------------------------------------------

    def save(self, body):
        if not supervisor.available():
            raise ApiError("no_supervisor", "The options can only be saved inside Home Assistant.", 503)
        draft = body.get("draft") or {}
        for pattern in draft.get("exclude", []):
            problem = matcher.check(pattern)
            if problem:
                raise ApiError("bad_pattern", f"{pattern}: {problem}")
        try:
            stored = supervisor.current_options()
            updated = dict(stored)
            for key in options.EDITABLE:
                if key in draft:
                    updated[key] = draft[key]
            supervisor.save_options(updated)
        except supervisor.SupervisorError as problem:
            raise ApiError("save_failed", str(problem), 502) from problem
        log.info("The options were saved from the web interface.")
        return {"saved": True}


class Handler(BaseHTTPRequestHandler):
    application: Application = None
    server_version = "GitExporter"

    def log_message(self, *_):
        return

    # -- plumbing ------------------------------------------------------------------------------

    def _send(self, status, payload, content_type="application/json"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise ApiError("too_large", status=413)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except ValueError as error:
            raise ApiError("bad_json") from error

    def _allowed(self):
        return self.client_address[0] in ALLOWED_ADDRESSES

    def _handle(self, method):
        if not self._allowed():
            return self._send(403, {"error": "forbidden"})
        self.application.last_activity = time.monotonic()
        parts = urlsplit(self.path)
        path = parts.path
        # Ingress removes its prefix; a request that still has one (a saved link) is served as well.
        marker = path.find("/api/")
        if marker > 0 and path.startswith("/api/hassio_ingress/"):
            path = path[marker:]
        try:
            if path.startswith("/api/"):
                return self._send(200, self._api(method, path, parse_qs(parts.query)))
            return self._static(path)
        except ApiError as error:
            return self._send(error.status, {"error": error.code, "message": str(error)})
        except Exception as error:  # noqa: BLE001
            log.error(f"{method} {path} failed: {error}")
            return self._send(500, {"error": "internal", "message": str(error)})

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def _static(self, path):
        name = "index.html" if path in ("", "/") else path.lstrip("/")
        target = (WEB_DIR / name).resolve()
        if WEB_DIR.resolve() not in target.parents and target != WEB_DIR.resolve():
            return self._send(404, b"not found", "text/plain")
        if not target.is_file():
            return self._send(404, b"not found", "text/plain")
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        return self._send(200, target.read_bytes(), f"{content_type}; charset=utf-8" if content_type.startswith("text/") or content_type.endswith("javascript") else content_type)

    # -- the API -------------------------------------------------------------------------------

    def _api(self, method, path, query):
        app = self.application
        if method == "GET":
            if path == "/api/state":
                return app.state_view()
            if path == "/api/log":
                return {"lines": log.recent()}
            if path == "/api/job":
                return app.job_view(query.get("id", [""])[0])
            if path == "/api/diff":
                return app.diff(query.get("job", [""])[0], query.get("repository", [""])[0], query.get("path", [""])[0])
            raise ApiError("not_found", status=404)

        body = self._body()
        if path == "/api/tree":
            return app.tree(body)
        if path == "/api/summary":
            return app.summary(body)
        if path == "/api/pattern":
            return app.pattern_effect(body)
        if path == "/api/save":
            return app.save(body)
        if path == "/api/preview" or path == "/api/export":
            settings = app.settings(body.get("draft") if path == "/api/preview" else None)
            wanted = body.get("repository")
            repositories = [app.find(settings, wanted)] if wanted else [r for r in settings.repositories if r.enabled]
            if not repositories:
                raise ApiError("no_repository", status=404)
            flags = {"settings": settings}
            if path == "/api/export":
                flags.update(accept_public_remote=bool(body.get("accept_public_remote")), remember=bool(body.get("remember")))
            job = app.start_job("preview" if path == "/api/preview" else "export", repositories, **flags)
            return {"job": job.id}
        if path == "/api/visibility":
            settings = app.settings()
            repository = app.find(settings, body.get("repository"))
            found = visibility.check(gitops.Repository(repository))
            return found.as_dict()
        if path == "/api/forget-public":
            settings = app.settings()
            state.forget_public_remote(app.find(settings, body.get("repository")).slug)
            return {"ok": True}
        if path == "/api/keep-running":
            app.keep_running = bool(body.get("value"))
            return {"ok": True}
        if path == "/api/stop":
            threading.Thread(target=supervisor.stop_self, daemon=True).start()
            return {"ok": True}
        raise ApiError("not_found", status=404)


def serve(application, port):
    Handler.application = application
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

