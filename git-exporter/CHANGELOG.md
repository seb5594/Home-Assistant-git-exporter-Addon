# Changelog

## 1.18.0

- Rename the app to Home Assistant Git Exporter and replace the development version.
- Use the shared startup helper from the private workflow engine.
- Replace legacy upstream CI with five-architecture validation and GHCR releases.
- Update the Alpine base and replace obsolete package pins and pip dependencies.
- Fix first-run Git initialization and honor pull-before-push and SSL verification.
- Keep exclude patterns containing spaces intact.
- Preserve exported app options instead of deleting them during synchronization.
- Run the configured secret scan before committing or pushing.
- Support JSON directory conversion with or without a trailing slash.
