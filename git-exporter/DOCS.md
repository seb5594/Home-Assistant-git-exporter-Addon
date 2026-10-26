# Home Assistant Git Exporter

Exports your Home Assistant configuration into one or more git repositories and keeps them up to date.
A web interface (**Open Web UI**) shows what would be exported before anything leaves your system, which
files the exclude rules keep out, and lets you change those rules with a click.

**This is a beta version (2.0.0).** Updating from 1.x needs no action, see [Updating from version 1](#updating-from-version-1).

## Contents

* [Quick start](#quick-start)
* [How an export works](#how-an-export-works)
* [Public and private repositories](#public-and-private-repositories)
* [The web interface](#the-web-interface)
* [Excluding files](#excluding-files)
* [What is exported, and where it goes](#what-is-exported-and-where-it-goes)
* [Checks and censoring](#checks-and-censoring)
* [Options](#options)
* [Updating from version 1](#updating-from-version-1)
* [Limitations](#limitations)
* [Troubleshooting](#troubleshooting)

## Quick start

1. Create an empty repository at your git host (GitHub, GitLab, Gitea, Bitbucket or your own server) and a
   personal access token with write access to it.
2. Open the configuration of this app, add a repository under **Repositories** and fill in **Name**,
   **Address** (`https://…`), **Who is it for**, **User name** and **Access token**.
   Decide carefully on *Who is it for*: [public or private](#public-and-private-repositories).
3. Start the app and open **Open Web UI**. Run a **Preview** first, look at the **Files** tab, add the
   patterns you want under **Excludes** and save.
4. **Export now**, or start the app from an automation: by default it exports every repository when it starts
   and stops itself ten idle minutes later.

For the Gitea app by alexbelgium use the address `http://db21ed7f-gitea:3000/<user>/<repository>.git`.

## How an export works

For each repository the app brings its working copy up to date (clone or fetch), checks who can see the
remote, builds the files that belong into the repository, compares them with the working copy, writes the
difference, commits and pushes. Nothing in `/config` or elsewhere is ever changed: the Home Assistant folders
are mounted read-only.

A file that is no longer exported (it was deleted, or an exclude pattern now covers it) is removed from the
repository with the next export. The git history keeps it.

Several repositories are exported one after the other. Each is built separately, so a public repository gets
censored files while a private one gets the originals.

## Public and private repositories

Every repository says whom it is for:

| | **public** | **private** |
| --- | --- | --- |
| `secrets.yaml` | Emptied: same keys and comments, no values | Exported as it is |
| Other files | Censored: secret values, IP and MAC addresses, secret-like keys, passwords in URLs, e-mail addresses | Exported as they are |
| Private keys | The file is not exported | The file is not exported (they are excluded by a preset) |
| Remote check | None | The host is asked whether the repository is public |

An entry without a choice is treated as public, and so is the repository of version 1.

### What happens when a private repository is public

Before a private repository is written to, the app asks the git host (through its API, or by an anonymous
clone test) whether anyone can read it. If so, **nothing is pushed**. The web interface shows a warning on the
repository and offers:

* *Push anyway, once* for this export,
* *Push anyway and do not ask again* to remember your decision (undo it with *Ask again from now on*).

An export that started on its own (the app was started by an automation) is held and logged; it does not guess.
With the option **Allow a public repository for private use** you decide in advance. If the host cannot be
asked, you are told and the export goes on.

## The web interface

* **Overview**: your repositories with their last result, a button for a visibility check, preview and export,
  and the decisions to make.
* **Preview**: a complete export without writing or pushing, as a list of new, changed and removed files. Click
  a file for its diff; values from `secrets.yaml` are shown as `••••`. Unsaved changes are included.
* **Files**: the whole tree of the folders the app can see. Every entry shows whether it is exported and which
  rule left it out; **Summary of the top level** counts files and sizes. **Exclude** and **Keep** add a pattern
  to your draft.
* **Excludes**: presets, your patterns with a test (*how many files would this change?*), the size limit and the
  parts that are exported.
* **Checks**: the censoring for public repositories and its allow list.
* **Log**: the recent lines of the app log.

Changes in *Files* and *Excludes* are a draft. Every tab shows the draft, and **Save to the app configuration**
stores it in the options of this app (it is the same as editing them on the configuration page).

The page is available in English and German, depending on the language of the browser.

### Stopping

After the export the app stays for **Stop after idle minutes** (10 by default) so that the web interface can be
used, then stops itself. Use **Keep the app running** to keep it. The value 0 stops right after the export, as
version 1 did; the web interface is then only reachable while you start the app yourself.

## Excluding files

Patterns are written like a `.gitignore` file:

| Pattern | Means |
| --- | --- |
| `*.db` | a name at any depth |
| `deps/` | a folder, at any depth, with everything in it |
| `/tts/` | a folder at the top of the exported folder |
| `custom_components/foo` | a path (a slash anywhere makes it relative to the top) |
| `**/cache/*.tmp` | `**` crosses folders, `*` and `?` do not |
| `!keep.yaml` | keep what an earlier pattern left out |

The last matching pattern wins, and your own patterns come after the presets, so `!` keeps something back from a
preset. A pattern applies to every exported folder; start it with `/` to anchor it at the top of each.

The presets are on by default:

| Preset | Leaves out |
| --- | --- |
| Databases | `*.db`, `*.sqlite*`, `*.sql` and more, including the recorder database |
| Log files | `*.log`, `*.log.*`, `*_log.txt` |
| Caches and temporary files | `__pycache__/`, `*.pyc`, `deps/`, `*.tmp`, `.DS_Store` and more |
| Runtime state of Home Assistant | `.ha_run.lock`, `.HA_VERSION`, `known_devices.yaml`, `ip_bans.yaml` and more |
| Generated content | `tts/`, `image/`, `camera/`, `snapshots/` |
| Credentials | `secrets.env`, `.env`, `*.token`, `.ssh/`, `*.kdbx`, `*.ovpn` and more |
| Keys and certificates | `*.key`, `*.pem`, `*.crt`, `*.p12`, `id_rsa*` and more |
| Audio and video | `*.mp3`, `*.wav`, `*.mp4`, `*.mkv` and more |
| Archives | `*.zip`, `*.tar*`, `*.gz`, `*.7z` and more |
| Copies and old versions | `*.bak`, `*.backup*`, `*.old*`, `*.orig`, `backups/` |
| Custom integrations and cards | `custom_components/`, `www/community/` (HACS downloads) |
| Development leftovers | `node_modules/`, `.venv/`, `notebooks/`, `.idea/` |
| Runtime data of apps | `*/db/`, `*/data/`, `*/cache/`, `*/logs/`, `*/ssl/` … in the app configuration folders |

Two more rules are not options: **Home Assistant's own state is never exported** (`.storage/`, `.cloud/`, `.uuid`,
`home-assistant_v2.db*`; they hold access tokens), and **files larger than the size limit** (5 MB by default) are
left out.

To keep an integration of your own while HACS downloads stay out, exclude `/custom_components/*` and add
`!/custom_components/my_integration` (or switch the preset off and exclude single folders).

## What is exported, and where it goes

| Source | Folder in the repository | Notes |
| --- | --- | --- |
| Home Assistant configuration (`/homeassistant` or `/config`) | `config/` | `esphome/` and `node-red/` go to their own folders |
| Lovelace dashboards | `lovelace/` | from `.storage`, as YAML |
| Options of the installed apps and the app repositories | `addons/` | needs the Supervisor |
| App configuration folders (`/app_configs` or `/addon_configs`) | `addons_config/` | |
| ESPHome | `esphome/` | `*.yaml`, `*.disabled`, `.gitignore`, `secrets.yaml` |
| Node-RED | `node-red/` | `flows.json` and `settings.js` only; credentials are never exported |
| Local apps (`/local_apps`, `/addons` or `/local_addons`) | `local_apps/` | off by default |

Home Assistant renamed `/addon_configs` to `/app_configs` and `/addons` to `/local_apps`. The app looks for
the new name first and for the old ones after it, so it works with both. The folder names in the repository
stay as they were to keep the history of existing repositories tidy; `local_apps/` is new.

## Checks and censoring

For public repositories every text file is checked before it is written:

* **Secrets**: the values of `secrets.yaml` are read with a YAML parser (block scalars such as `>-` templates,
  nested entries, lists, comments and tags such as `!env_var` are understood) and replaced wherever they appear:
  by `!secret name` when a file's whole value is a top-level secret, otherwise by `<censored>`. Values from the
  option **Extra secret values** are handled the same way.
* **Keys** named like secrets (`password`, `token`, `api_key`, `client_id`, `chat_id`, `latitude`, `longitude`
  and more) lose their value unless it is a `!secret`, `!include` or a template.
* **URLs with a password** and **e-mail addresses** are censored.
* **IP and MAC addresses** (IPv4 and IPv6) are replaced by addresses from the documentation ranges
  (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`, `2001:db8::/32`, `00-00-5E-00-53-…`). The same address
  always becomes the same placeholder, so the files still show which entries belong together. Four numbers
  after `version:`, netmasks and well-known DNS servers such as `8.8.8.8` are left alone.
* A file with a **private key** is not exported at all.

With **When something is found: block** the export of that repository stops instead of censoring. Texts in
**Allowed values** are never censored. Binary files are not touched.

The *Preview* tab shows how much was censored per category and per file.

## Options

The configuration page has these groups (each option has a description there, in English and German):

* **Repositories**: `name`, `url`, `audience` (`public` or `private`), `username`, `password` (access token),
  `email`, `branch`, `provider`, `commit_message` (`{DATE}` is replaced), `pull_before_push`,
  `ssl_verification`, `check_visibility`, `allow_public_remote`, `enabled`.
* **Export**: `lovelace`, `addons`, `addon_configs`, `esphome`, `node_red`, `local_apps`.
* **Presets**: one switch for each preset above.
* **Exclude**: your own patterns. **Secrets** and **Allowed secrets**: extra values to censor, and values never to censor.
* **Check**: `enabled`, `check_for_secrets`, `check_for_ips`, `on_finding` (`censor` or `block`).
* **Limits**: `max_file_size_mb`.
* **Behavior**: `export_on_start`, `stop_after_minutes`, `keep_running`.

Only the https and http addresses of repositories are supported, no SSH. The access token is sent as HTTP basic
authentication and is not stored in the git configuration of the working copy.

## Updating from version 1

* The app keeps its name, its address and its architectures (`amd64`, `aarch64`, `armv7`, `armhf`, `i386`), so
  it is updated like always.
* The single `repository` of version 1 becomes the first entry of `repositories`, named `default`, marked as
  **public**. You can rename it and switch it to private on the configuration page.
* The `dry_run` option is gone. Use the **Preview** tab instead.
* Your `exclude` list stays and is applied on top of the presets. Because excluded files now also leave the
  repository, the first export removes what earlier versions copied and your rules or presets cover (databases,
  logs, `custom_components`, …). The history keeps all of it. Run a **Preview** first to see the list.
* By default the app now stays for ten idle minutes after an export. Set **Stop after idle minutes** to 0 for the
  old behaviour.
* The folders in the repository are the same as before.

## Limitations

* Only https and http, no SSH.
* The censoring is pattern based. It finds what it is told to look for; read the preview of a repository that is
  meant for the public before the first push, and prefer a private repository for anything you are unsure about.
* Block scalars in files other than `secrets.yaml` are censored line by line, so a secret that stretches over
  several lines is only found when it is a value of `secrets.yaml` or an extra secret.
* The visibility check depends on what the host tells; behind a firewall an anonymous test can say *public*
  although only your network can reach it.

## Troubleshooting

**Nothing is pushed and the overview shows a warning.** The repository is meant for private use but is
public. See [What happens when a private repository is public](#what-happens-when-a-private-repository-is-public).

**"Authentication failed" or "terminal prompts disabled".** The user name or token is wrong, or the token has
no write access. Check the token and, for a self-hosted server, the address.

**Certificate errors.** A server with a self-signed certificate needs *Check the certificate* switched off for
that repository. Anything you send is then readable on the way; prefer a trusted certificate.

**The Home Assistant configuration is empty or `/config` is not found.** The app looks for `/homeassistant` and
`/config`. Both are mounted by the app; if neither exists the Supervisor could not provide it.

**An integration of mine is missing.** The preset *Custom integrations and cards* leaves `custom_components` out.
See [Excluding files](#excluding-files) for how to keep your own.

**The log says a value of secrets.yaml could not be read.** The file is not valid YAML. The app still uses the
lines it can read; fix the file to be sure everything is found.
