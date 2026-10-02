# Home Assistant Git Exporter

<!-- badges:begin (generated from project metadata) -->
[![version](https://img.shields.io/static/v1?label=version&message=1.19.0&color=1877A5&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/releases) [![released](https://img.shields.io/github/release-date-pre/seb5594/Home-Assistant-git-exporter-Addon?label=released&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/releases) [![build](https://img.shields.io/github/actions/workflow/status/seb5594/Home-Assistant-git-exporter-Addon/ci.yml?branch=main&label=build&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/actions/workflows/ci.yml)<br>
[![stars](https://img.shields.io/github/stars/seb5594/Home-Assistant-git-exporter-Addon?label=stars&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/stargazers) [![issues](https://img.shields.io/github/issues/seb5594/Home-Assistant-git-exporter-Addon?label=issues&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/issues) [![updated](https://img.shields.io/github/last-commit/seb5594/Home-Assistant-git-exporter-Addon?label=updated&style=flat)](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/commits/main) ![image pulls](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fseb5594%2FHome-Assistant-git-exporter-Addon%2Fbadges%2Fimage-pulls.json&style=flat)<br>
![arch](https://img.shields.io/static/v1?label=arch&message=amd64%20%C2%B7%20aarch64%20%C2%B7%20armv7%20%C2%B7%20armhf%20%C2%B7%20i386&color=157F71&style=flat)<br>
![mounts (read-write)](https://img.shields.io/static/v1?label=mounts%20%28read-write%29&message=app%20configs%20%C2%B7%20config&color=B45309&style=flat)<br>
![stage](https://img.shields.io/static/v1?label=stage&message=stable&color=2F855A&style=flat) ![options](https://img.shields.io/static/v1?label=options&message=18&color=1877A5&style=flat)<br>
![image size](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fseb5594%2FHome-Assistant-git-exporter-Addon%2Fbadges%2Fimage-size.json&style=flat) ![runtime tests](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fseb5594%2FHome-Assistant-git-exporter-Addon%2Fbadges%2Fruntime-tests.json&style=flat) ![last build](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fseb5594%2FHome-Assistant-git-exporter-Addon%2Fbadges%2Flast-build.json&style=flat)<br>
[![Home Assistant](https://img.shields.io/static/v1?label=Home%20Assistant&message=Add%20app%20repository&color=18BCF2&style=flat&logo=homeassistant&logoColor=white)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-Apps)
<!-- badges:end -->

Git Exporter is a Home Assistant app that copies your configuration into a Git repository you choose: `/config`, Lovelace dashboards, ESPHome and Node-RED files, and the options of your other apps. Every change becomes a commit, so you get a readable history and can restore any earlier state. It runs once per start, for example from an automation, blanks `secrets.yaml` values in the export and can scan for secrets and IP addresses before it commits.

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

CI builds all five architectures (`amd64` and `aarch64` on the current Home Assistant base image, `armv7`, `armhf` and `i386` on its previous generation) and checks the actual exporter runtime and the shared entrypoint. The badges above show the real app version, mounts, and capabilities from `git-exporter/config.yaml`, plus image sizes and test counts published by the pipeline. GitHub does not provide Home Assistant installation numbers or countries.

This app runs once and then exits; it has no ingress web UI.

Based on the original Git Exporter work from the Home Assistant add-on community. Maintained by [seb5594](https://github.com/seb5594).

<!-- support:begin (generated, shared text) -->
## Say thanks

All my projects are built in my spare time, just for the fun of it. Still, they take a lot of time and care, and many of the smart home gadgets I buy end up here because I want to make them cloud-free and smart-home ready. Every bit of support means a lot to me.

If my work helped you or turned out to be useful, show your appreciation with a hot drink for my next sleepless night.

[![Buy Me a Coffee](https://img.shields.io/static/v1?label=Support&message=Buy%20Me%20a%20Coffee&color=FFDD00&logo=buy-me-a-coffee&logoColor=black&style=for-the-badge)](https://buymeacoffee.com/seb5594) [![PayPal](https://img.shields.io/static/v1?label=Support&message=PayPal&color=0070BA&logo=paypal&logoColor=white&style=for-the-badge)](https://www.paypal.com/donate/?hosted_button_id=QMQPNRENXDN26)
<!-- support:end -->
