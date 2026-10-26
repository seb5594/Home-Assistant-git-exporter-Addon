# Changelog

## 2.0.0-beta.1

A new major version, rewritten around a web interface. Updating needs no action: the single repository of
version 1 moves into the new list of repositories by itself, the app keeps its name, its address
(`git-exporter`) and all five architectures.

**New**

* **Web interface** (Open Web UI, or *Git Exporter* in the sidebar):
  * *Preview* runs a complete export without writing or pushing and lists the files that are new,
    changed or removed, with a diff for each. It replaces the `dry_run` option.
  * *Files* shows the whole file tree of everything the app can see and what the exclude rules do to each
    entry, with the rule that left it out.
  * *Excludes* has presets for what does not belong into a repository (databases, logs, caches, keys,
    credentials, large media, HACS downloads and more), your own patterns, a size limit and a test that tells
    how many files a pattern would change. Unsaved changes show in Files and Preview right away; *Save* writes
    them to the app configuration.
* **Any number of repositories**: GitHub, GitLab, Gitea, Bitbucket or your own server side by side, each with
  its own login, branch and commit message.
* **Public or private per repository.** A public repository gets nothing private: secrets.yaml is emptied
  (comments and structure stay), values from secrets.yaml, IP and MAC addresses, secret-like keys, passwords in
  URLs and e-mail addresses are censored in every file. A private repository gets the files as they are,
  secrets.yaml included. Before a private repository is written to, the app asks the git host whether it is
  public and, if it is, holds the push and lets you decide in the web interface.
* New folders: `/local_apps` (formerly `/local_addons` or `/addons`) and `/app_configs` (formerly
  `/addon_configs`). Both names are found; the Home Assistant folders are mounted read-only now.
* New logo and icon with the Git logo. The configuration is translated into English and German completely.

**Fixed**

* The secret check no longer stalls or fails on a secrets.yaml with block scalars (`>-` templates), nested
  entries or comments: the file is read with a YAML parser instead of being cut into patterns.
* The IP check no longer reports version numbers, netmasks or well-known DNS servers, and it understands IPv6
  and MAC addresses. Addresses are replaced instead of stopping the export.
* Files that are excluded now also leave the repository when they were exported by an earlier version
  (databases, logs, third-party code): the old exporter kept them forever.
* Credentials are no longer part of the remote address in the repository's git configuration.

**Changed**

* The app stays reachable for a while after the export (option *Stop after idle minutes*, 10 by default; 0
  stops right after the export like before).
* The repository of version 1 is marked as *public*: it was always exported with an emptied secrets.yaml.
* The exporter is plain Python and git now. `rsync`, `git-secrets`, `grep`, `sed`, `make` and `findutils` are gone
  from the image.
* The repository folders `config`, `lovelace`, `esphome`, `node-red`, `addons` and `addons_config` keep their
  names; new is `local_apps`.

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
