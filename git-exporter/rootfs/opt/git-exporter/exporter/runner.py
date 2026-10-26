"""One export of one repository: bring the clone up to date, check the remote, build, compare, write, push.

Every result is a dictionary with a `status` and a message `code` plus `args`. The web interface turns
the code into a sentence in the language of the browser, the log gets the English text from `describe`.
"""
import time

from . import export, gitops, log, sanitize, sources, state, visibility

STATUS_OK = "ok"
STATUS_HELD = "held"
STATUS_BLOCKED = "blocked"
STATUS_ERROR = "error"
STATUS_SKIPPED = "skipped"

TEXTS = {
    "pushed": "Exported {changes} changes and pushed them.",
    "nothing": "Nothing changed; there was nothing to commit.",
    "committed_local": "Committed {changes} changes. Nothing was pushed because the remote is unchanged.",
    "preview": "Preview: {added} new, {modified} changed, {removed} removed files.",
    "held_public_remote": "This repository is meant for private use, but its remote is public. Nothing was pushed. "
                          "Open the web interface of this app to decide.",
    "blocked_findings": "The export was stopped: {count} private values were found and the repository is set to block.",
    "error": "{message}",
    "no_url": "No address is set for this repository.",
    "disabled": "This repository is switched off.",
    "no_sources": "Nothing to export: no source folder is available.",
}


def describe(result):
    text = TEXTS.get(result.get("code"), result.get("code", ""))
    try:
        return text.format(**result.get("args", {}))
    except (KeyError, IndexError):
        return text


def _result(repository, mode, status, code, started, **extra):
    args = extra.pop("args", {})
    return {"repository": repository.name, "slug": repository.slug, "mode": mode, "status": status, "code": code,
            "args": args, "audience": repository.audience, "seconds": round(time.monotonic() - started, 1), "finished": export.timestamp(), **extra}


def _secret_values(settings):
    """Values to hide when a diff is shown: the secrets of secrets.yaml and the extra ones from the options."""
    values = {secret.value for secret in sanitize.parse_secrets(export._read_secrets(settings))[0]}
    values.update(settings.secrets)
    return [value for value in values if len(value) >= sanitize.MIN_SECRET_LENGTH]


def run(settings, repository, dry_run=False, accept_public_remote=False, remember=False, progress=None):
    """Runs one repository. Returns (result, plan); the plan is None when nothing got that far."""
    started = time.monotonic()
    mode = "preview" if dry_run else "export"
    if not repository.enabled:
        return _result(repository, mode, STATUS_SKIPPED, "disabled", started), None
    if not repository.url:
        return _result(repository, mode, STATUS_ERROR, "no_url", started), None
    if not sources.active(settings):
        return _result(repository, mode, STATUS_ERROR, "no_sources", started), None

    clone = gitops.Repository(repository)
    try:
        if progress:
            progress("repository")
        clone.prepare()
    except (gitops.GitError, OSError) as problem:
        if not (dry_run and (clone.directory / ".git").exists()):
            return _result(repository, mode, STATUS_ERROR, "error", started, args={"message": str(problem)}), None

    found = None
    if repository.check_visibility:
        if progress:
            progress("visibility")
        found = visibility.check(clone)
    accepted = state.public_remote_accepted(repository.slug, clone.url)
    action, reason = ("go", "")
    if found:
        action, reason = visibility.decision(repository, found, accepted or accept_public_remote)
    extra = {"visibility": found.as_dict() if found else None}
    if accept_public_remote and remember and found and found.state == "public":
        state.acknowledge_public_remote(repository.slug, clone.url)

    if progress:
        progress("collect")
    collected = export.collect(settings, repository, progress)
    plan = export.plan(collected, str(clone.directory))
    extra.update(counts=plan.counts(), findings=dict(collected.findings), warnings=collected.warnings,
                 blocked_files=collected.blocked, too_large=collected.too_large)
    changes = len(plan.changes)

    if dry_run:
        extra["held"] = action == "hold"
        return _result(repository, mode, STATUS_OK, "preview", started, args=plan.counts(), **extra), plan

    if action == "hold":
        return _result(repository, mode, STATUS_HELD, "held_public_remote", started, **extra), plan
    if repository.public and settings.check["on_finding"] == "block" and collected.findings:
        count = sum(collected.findings.values())
        return _result(repository, mode, STATUS_BLOCKED, "blocked_findings", started, args={"count": count}, **extra), plan

    try:
        if progress:
            progress("write")
        export.apply(plan, str(clone.directory))
        message = repository.commit_message.replace("{DATE}", export.timestamp())
        committed = clone.commit_all(message)
        if committed or clone.has_unpushed_commits():
            if progress:
                progress("push")
            clone.push()
            code = "pushed"
        else:
            code = "nothing"
    except (gitops.GitError, OSError) as problem:
        return _result(repository, mode, STATUS_ERROR, "error", started, args={"message": str(problem)}, **extra), plan
    return _result(repository, mode, STATUS_OK, code, started, args={"changes": changes}, **extra), plan


def remember_result(result):
    state.update(result["slug"], last_run={k: v for k, v in result.items() if k != "blocked_files"})


def run_all(settings, progress=None):
    """An export of every repository that is switched on, one after the other."""
    results = []
    for repository in settings.repositories:
        log.info(f"Exporting {repository.name} ({'public' if repository.public else 'private'} repository)...")
        result, _plan = run(settings, repository, progress=progress)
        remember_result(result)
        level = log.info if result["status"] in (STATUS_OK, STATUS_SKIPPED) else log.warning
        level(f"{repository.name}: {describe(result)}")
        for code, args in result.get("warnings", []):
            log.warning(f"{repository.name}: {code} {args}")
        results.append(result)
    return results
