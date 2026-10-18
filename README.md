<!-- header:begin (generated from project metadata) -->
<h1 align="center">Home Assistant Git Exporter</h1>

<p align="center">
  <img src="https://raw.githubusercontent.com/seb5594/Home-Assistant-git-exporter-Addon/main/git-exporter/logo.png" alt="Home Assistant Git Exporter" width="218" height="160">
</p>

---

<p align="center">
  <a href="https://paypal.me/seb5594"><img src="https://img.shields.io/static/v1?label=Support&amp;message=PayPal&amp;color=0070BA&amp;logo=paypal&amp;logoColor=white&amp;style=for-the-badge" alt="PayPal" height="40"></a>
  <a href="https://buymeacoffee.com/seb5594"><img src="https://img.shields.io/static/v1?label=Support&amp;message=Buy%20Me%20a%20Coffee&amp;color=FFDD00&amp;logo=buy-me-a-coffee&amp;logoColor=black&amp;style=for-the-badge" alt="Buy Me a Coffee" height="40"></a>
</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-Apps"><img src="https://img.shields.io/static/v1?label=Home%20Assistant&amp;message=Add%20app%20repository&amp;color=18BCF2&amp;logo=homeassistant&amp;logoColor=white&amp;style=for-the-badge" alt="Home Assistant" height="28"></a>
  <a href="https://github.com/seb5594/Home-Assistant-git-exporter-Addon/releases/tag/v1.18.1"><img src="https://img.shields.io/static/v1?label=version&amp;message=1.18.1&amp;color=1877A5&amp;style=for-the-badge" alt="version" height="28"></a>
</p>

<p align="center">
  <a href="https://github.com/seb5594/Home-Assistant-git-exporter-Addon/stargazers"><img src="https://img.shields.io/github/stars/seb5594/Home-Assistant-git-exporter-Addon?label=stars&amp;style=flat" alt="stars" height="20"></a>
  <a href="https://github.com/seb5594/Home-Assistant-git-exporter-Addon/issues"><img src="https://img.shields.io/github/issues/seb5594/Home-Assistant-git-exporter-Addon?label=issues&amp;style=flat" alt="issues" height="20"></a>
  <a href="https://github.com/seb5594/Home-Assistant-git-exporter-Addon/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/seb5594/Home-Assistant-git-exporter-Addon/ci.yml?branch=main&amp;label=checks&amp;style=flat" alt="checks" height="20"></a>
  <a href="https://github.com/seb5594/Home-Assistant-git-exporter-Addon#license"><img src="https://img.shields.io/github/license/seb5594/Home-Assistant-git-exporter-Addon?label=license&amp;style=flat" alt="license" height="20"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/static/v1?label=arch&amp;message=amd64%20%C2%B7%20aarch64%20%C2%B7%20armv7%20%C2%B7%20armhf%20%C2%B7%20i386&amp;color=157F71&amp;style=flat" alt="arch" height="20">
  <img src="https://img.shields.io/static/v1?label=mounts%20%28read-write%29&amp;message=app%20configs%20%C2%B7%20config&amp;color=B45309&amp;style=flat" alt="mounts (read-write)" height="20">
  <img src="https://img.shields.io/static/v1?label=stage&amp;message=stable&amp;color=2F855A&amp;style=flat" alt="stage" height="20">
  <img src="https://img.shields.io/static/v1?label=options&amp;message=18&amp;color=1877A5&amp;style=flat" alt="options" height="20">
</p>
<!-- header:end -->

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

CI builds all five architectures (`amd64` and `aarch64` on the current Home Assistant base image, `armv7`, `armhf` and `i386` on its previous generation) and checks the actual exporter runtime and the shared entrypoint. The badges above show the real app version, mounts, and capabilities from `git-exporter/config.yaml`, plus image sizes, test counts and GHCR pulls measured by the pipeline. GitHub does not provide Home Assistant installation numbers or countries.

This app runs once and then exits; it has no ingress web UI.

Based on the original Git Exporter work from the Home Assistant add-on community. Maintained by [seb5594](https://github.com/seb5594).

<!-- support:begin (generated, shared text) -->
## Say thanks

All my projects are built in my spare time, just for the fun of it. Still, they take a lot of time and care, and many of the smart home gadgets I buy end up here because I want to make them cloud-free and smart-home ready. Every bit of support means a lot to me.

If my work helped you or turned out to be useful, show your appreciation with a hot drink for my next sleepless night.

[![PayPal](https://img.shields.io/static/v1?label=Support&message=PayPal&color=0070BA&logo=paypal&logoColor=white&style=for-the-badge)](https://paypal.me/seb5594) [![Buy Me a Coffee](https://img.shields.io/static/v1?label=Support&message=Buy%20Me%20a%20Coffee&color=FFDD00&logo=buy-me-a-coffee&logoColor=black&style=for-the-badge)](https://buymeacoffee.com/seb5594)
<!-- support:end -->

<!-- license:begin (generated from the license file) -->
## License

[![license](https://img.shields.io/static/v1?label=license&message=Apache-2.0&color=5B6770&style=flat)](LICENSE)

Published under the [Apache License 2.0](LICENSE).
<!-- license:end -->
