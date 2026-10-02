# Home Assistant Git Exporter

<!-- badges:begin (generated from project metadata) -->
[![Version](https://img.shields.io/badge/version-1.18.1-1877A5?style=for-the-badge)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/seb5594/Home-Assistant-git-exporter-Addon/ci.yml?branch=main&label=builds)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/actions/workflows/ci.yml)
[![Release asset downloads](https://img.shields.io/github/downloads/seb5594/Home-Assistant-git-exporter-Addon/total?label=release%20downloads)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/releases)
[![Stars](https://img.shields.io/github/stars/seb5594/Home-Assistant-git-exporter-Addon?label=stars)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/seb5594/Home-Assistant-git-exporter-Addon?label=updated)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/commits/main)

![armhf](https://img.shields.io/badge/armhf-supported-157F71?style=flat-square) ![armv7](https://img.shields.io/badge/armv7-supported-157F71?style=flat-square) ![aarch64](https://img.shields.io/badge/aarch64-supported-157F71?style=flat-square) ![amd64](https://img.shields.io/badge/amd64-supported-157F71?style=flat-square) ![i386](https://img.shields.io/badge/i386-supported-157F71?style=flat-square)
![stage](https://img.shields.io/badge/stage-stable-2F855A?style=flat-square) ![mount](https://img.shields.io/badge/mount-config-157F71?style=flat-square) ![mount](https://img.shields.io/badge/mount-app%20configs-157F71?style=flat-square)

[![Add to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-Apps)
[![Buy Me a Coffee](https://img.shields.io/badge/Support-Buy%20Me%20a%20Coffee-FFDD00?logo=buy-me-a-coffee&logoColor=black&style=for-the-badge)](https://buymeacoffee.com/seb5594)
[![PayPal](https://img.shields.io/badge/Support-PayPal-0070BA?logo=paypal&logoColor=white&style=for-the-badge)](https://www.paypal.com/donate/?hosted_button_id=QMQPNRENXDN26)
<!-- badges:end -->

Keep a readable history of your Home Assistant configuration in a Git repository you control. Exporters for Lovelace, ESPHome, Node-RED, app settings, and app configurations are optional; choose the files worth tracking.

## What it exports

| Source | Result |
| --- | --- |
| `/config` | Home Assistant configuration; `secrets.yaml` values are blanked in the export |
| Lovelace storage | YAML representations of configured dashboards |
| ESPHome and Node-RED | Selected configuration and flow files |
| Supervisor apps and repositories | App options and repository list |
| `/addon_configs` | Other apps' exposed configuration folders |

Excluded patterns skip files you do not want to track. When enabled, the secret checks scan staged changes before a commit or push; inspect the destination repository before making it public. Configure the Git destination and choose which exports to run in Home Assistant.

**[Configuration and options](git-exporter/DOCS.md)** · **[Changelog](git-exporter/CHANGELOG.md)** · **[Releases and image references](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/releases)**

## Release and statistics

CI checks the five declared architectures, the actual exporter runtime, and the shared entrypoint. Badges show the real app version, configured mounts, CI status, and GitHub release-asset downloads. GitHub does not provide GHCR pull counts, Home Assistant installation numbers, or countries for these downloads.

The legacy 32-bit builds are provided for systems whose Supervisor still supports them. This app runs once and then exits; it has no ingress web UI.

Based on the original Git Exporter work from the Home Assistant add-on community. Maintained by [seb5594](https://github.com/seb5594).
