# Home Assistant Git Exporter

<!-- badges:begin (generated from project metadata) -->
[![version](https://img.shields.io/static/v1?label=version&message=1.18.1&color=1877A5&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/releases) [![released](https://img.shields.io/github/release-date-pre/seb5594/Home-Assistant-git-exporter-Addon?label=released&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/releases) [![build](https://img.shields.io/github/actions/workflow/status/seb5594/Home-Assistant-git-exporter-Addon/ci.yml?branch=main&label=build&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/actions/workflows/ci.yml)

[![stars](https://img.shields.io/github/stars/seb5594/Home-Assistant-git-exporter-Addon?label=stars&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/stargazers) [![forks](https://img.shields.io/github/forks/seb5594/Home-Assistant-git-exporter-Addon?label=forks&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/forks) [![issues](https://img.shields.io/github/issues/seb5594/Home-Assistant-git-exporter-Addon?label=issues&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/issues) [![updated](https://img.shields.io/github/last-commit/seb5594/Home-Assistant-git-exporter-Addon?label=updated&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/commits/main) ![image pulls](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fseb5594%2FHome-Assistant-git-exporter-Addon%2Fbadges%2Fimage-pulls.json&style=flat)

![arch](https://img.shields.io/static/v1?label=arch&message=armhf&color=157F71&style=flat) ![arch](https://img.shields.io/static/v1?label=arch&message=armv7&color=157F71&style=flat) ![arch](https://img.shields.io/static/v1?label=arch&message=aarch64&color=157F71&style=flat) ![arch](https://img.shields.io/static/v1?label=arch&message=amd64&color=157F71&style=flat) ![arch](https://img.shields.io/static/v1?label=arch&message=i386&color=157F71&style=flat)

![read-write](https://img.shields.io/static/v1?label=read-write&message=config%20%C2%B7%20app%20configs&color=B45309&style=flat)

![stage](https://img.shields.io/static/v1?label=stage&message=stable&color=2F855A&style=flat) ![startup](https://img.shields.io/static/v1?label=startup&message=once&color=5B6770&style=flat) ![boot](https://img.shields.io/static/v1?label=boot&message=manual&color=5B6770&style=flat) ![supervisor api](https://img.shields.io/static/v1?label=supervisor%20api&message=manager&color=B45309&style=flat) ![options](https://img.shields.io/static/v1?label=options&message=18&color=1877A5&style=flat) ![base image](https://img.shields.io/static/v1?label=base%20image&message=base%3A3.22-2025.11.1&color=5B6770&style=flat)

![image size](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fseb5594%2FHome-Assistant-git-exporter-Addon%2Fbadges%2Fimage-size.json&style=flat) ![runtime tests](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fseb5594%2FHome-Assistant-git-exporter-Addon%2Fbadges%2Fruntime-tests.json&style=flat) ![last build](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fseb5594%2FHome-Assistant-git-exporter-Addon%2Fbadges%2Flast-build.json&style=flat)

[![Add to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-Apps) [![Buy Me a Coffee](https://img.shields.io/static/v1?label=Support&message=Buy%20Me%20a%20Coffee&color=FFDD00&logo=buy-me-a-coffee&logoColor=black&style=flat)](https://buymeacoffee.com/seb5594) [![PayPal](https://img.shields.io/static/v1?label=Support&message=PayPal&color=0070BA&logo=paypal&logoColor=white&style=flat)](https://www.paypal.com/donate/?hosted_button_id=QMQPNRENXDN26)
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

CI checks the five declared architectures, the actual exporter runtime, and the shared entrypoint. The badges above show the real app version, mounts, and capabilities from `git-exporter/config.yaml`, plus image sizes and test counts published by the pipeline. GitHub does not provide Home Assistant installation numbers or countries.

The legacy 32-bit builds are provided for systems whose Supervisor still supports them. This app runs once and then exits; it has no ingress web UI.

Based on the original Git Exporter work from the Home Assistant add-on community. Maintained by [seb5594](https://github.com/seb5594).
