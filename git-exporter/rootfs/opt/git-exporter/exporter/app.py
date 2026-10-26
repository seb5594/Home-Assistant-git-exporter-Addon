"""Starts the web interface, runs the export that is due and stops the app when nobody needs it any more."""
import os
import time

from . import log, options, runner, server, supervisor

VERSION_FILE = os.environ.get("VERSION_FILE", "/etc/git-exporter/version")
PORT = int(os.environ.get("INGRESS_PORT", "8099"))


def read_version():
    try:
        with open(VERSION_FILE, encoding="utf-8") as handle:
            return handle.read().strip()
    except OSError:
        return "unknown"


def load_settings():
    """The options as stored right now; the file is used when the Supervisor cannot be asked."""
    if supervisor.available():
        try:
            return options.parse(supervisor.current_options())
        except supervisor.SupervisorError:
            pass
    return options.parse(options.load_file())


def migrate_legacy_options():
    """Moves the single repository of version 1 into the list of repositories (once)."""
    if not supervisor.available():
        return
    try:
        stored = supervisor.current_options()
        settings = options.parse(stored)
        migrated = options.migrated_options(stored, settings)
        if migrated:
            supervisor.save_options(migrated)
            log.info("The repository of version 1 is now the first entry of the repository list "
                     "(marked as public, which is how it was exported before).")
    except supervisor.SupervisorError as problem:
        log.warning(f"The old repository settings could not be moved ({problem}); they are used as they are.")


def main():
    version = read_version()
    log.info(f"Starting Home Assistant Git Exporter {version}")
    migrate_legacy_options()
    application = server.Application(load_settings, version)
    server.serve(application, PORT)
    settings = load_settings()
    log.info(f"Web interface ready on port {PORT}. {len(settings.repositories)} repositories are set up.")
    if not settings.repositories:
        log.warning("No repository is set up yet. Add one in the configuration of the app.")

    exported = False
    if settings.behavior["export_on_start"] and any(r.enabled for r in settings.repositories):
        application.auto_result = runner.run_all(settings)
        exported = True

    # Whoever started the app to get an export (an automation, the old way) finds it stopped afterwards,
    # unless the web interface is in use: it stays for a number of idle minutes.
    application.last_activity = time.monotonic()
    while True:
        time.sleep(5)
        settings = load_settings()
        behavior = settings.behavior
        keep = behavior["keep_running"] if application.keep_running is None else application.keep_running
        busy = any(not job.done for job in application.jobs.values())
        if keep or busy:
            continue
        minutes = behavior["stop_after_minutes"]
        idle = time.monotonic() - application.last_activity
        if exported and minutes == 0 and idle > 15:
            break
        if minutes > 0 and idle > minutes * 60:
            break
    log.info("Nothing more to do. Stopping the app.")
    try:
        supervisor.stop_self()
    except supervisor.SupervisorError as problem:
        log.warning(f"The app could not stop itself ({problem}).")
    time.sleep(30)


if __name__ == "__main__":
    main()
