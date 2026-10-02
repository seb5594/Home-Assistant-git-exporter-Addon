# Changelog

## 1.19.0

- Build on the official multi-architecture Home Assistant base image `3.24-2026.08.0`; the per-architecture `build.yaml` is gone.
- Pin every installed Alpine package to an exact version.
- Keep every architecture: `armhf`, `armv7` and `i386` are built on the previous base image generation
  (`3.22-2025.11.1`), whose Alpine ships older package versions (pinned as `*_LEGACY` build arguments).
- Name release images `ARCH-hass-git-exporter-vVERSION`.

## 1.18.1

- Publish the tested five-architecture images through one shared pipeline and a multi-platform manifest.
- Add metadata-driven build, version, mount, and support badges.
- Share validation, release, and documentation templates with other Home Assistant projects.

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
