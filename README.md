<!-- header:begin (generated from project metadata) -->
<h1 align="center">Home Assistant Git Exporter</h1>

<p align="center">
  <img src="https://raw.githubusercontent.com/seb5594/Home-Assistant-git-exporter-Addon/main/git-exporter/logo.png" alt="Home Assistant Git Exporter" width="341" height="160">
</p>

---

<p align="center">
  <a href="https://paypal.me/seb5594"><img src="https://img.shields.io/static/v1?label=Support&amp;message=PayPal&amp;color=0070BA&amp;logo=paypal&amp;logoColor=white&amp;style=for-the-badge" alt="PayPal" height="40"></a>
  <a href="https://buymeacoffee.com/seb5594"><img src="https://img.shields.io/static/v1?label=Support&amp;message=Buy%20Me%20a%20Coffee&amp;color=FFDD00&amp;logo=buy-me-a-coffee&amp;logoColor=black&amp;style=for-the-badge" alt="Buy Me a Coffee" height="40"></a><br>
  <a href="https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-Apps"><img src="https://img.shields.io/static/v1?label=Home%20Assistant&amp;message=Add%20app%20repository&amp;color=18BCF2&amp;logo=homeassistant&amp;logoColor=white&amp;style=for-the-badge" alt="Home Assistant" height="28"></a>
  <a href="https://github.com/seb5594/Home-Assistant-git-exporter-Addon/releases/tag/v2.0.0-beta.1"><img src="https://img.shields.io/static/v1?label=version&amp;message=Beta%201&amp;color=1877A5&amp;style=for-the-badge" alt="version" height="28"></a>
  <img src="https://img.shields.io/static/v1?label=image%20pulls&amp;message=30&amp;color=1877A5&amp;style=for-the-badge" alt="image pulls" height="28"><br>
  <img src="https://img.shields.io/static/v1?label=arch%20%26%20size&amp;message=amd64%2089.1%20%C2%B7%20aarch64%20101.1%20%C2%B7%20armv7%2073.0%20%C2%B7%20armhf%2081.7%20%C2%B7%20i386%2084.7%20MiB&amp;color=157F71&amp;style=flat" alt="arch &amp; size" height="20">
  <img src="https://img.shields.io/static/v1?label=stage&amp;message=experimental&amp;color=2F855A&amp;style=flat" alt="stage" height="20">
  <img src="https://img.shields.io/static/v1?label=ingress&amp;message=enabled&amp;color=7C3AED&amp;style=flat" alt="ingress" height="20">
  <img src="https://img.shields.io/static/v1?label=mounts%20%28read-only%29&amp;message=app%20configs%20%C2%B7%20config%20%C2%B7%20local%20apps&amp;color=157F71&amp;style=flat" alt="mounts (read-only)" height="20"><br>
  <a href="https://github.com/seb5594/Home-Assistant-Apps/stargazers"><img src="https://img.shields.io/github/stars/seb5594/Home-Assistant-git-exporter-Addon?label=stars&amp;style=flat" alt="stars" height="20"></a>
  <a href="https://github.com/seb5594/Home-Assistant-Apps/issues"><img src="https://img.shields.io/github/issues/seb5594/Home-Assistant-git-exporter-Addon?label=issues&amp;style=flat" alt="issues" height="20"></a>
  <img src="https://img.shields.io/static/v1?label=runtime%20tests&amp;message=49%20passed&amp;color=2F855A&amp;style=flat" alt="runtime tests" height="20">
  <a href="https://github.com/seb5594/Home-Assistant-git-exporter-Addon/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/seb5594/Home-Assistant-git-exporter-Addon/ci.yml?branch=main&amp;label=checks&amp;style=flat" alt="checks" height="20"></a>
  <a href="https://github.com/seb5594/Home-Assistant-Apps#license"><img src="https://img.shields.io/github/license/seb5594/Home-Assistant-git-exporter-Addon?label=license&amp;style=flat" alt="license" height="20"></a>
</p>
<!-- header:end -->

Exports your Home Assistant configuration to one or more git repositories (GitHub, GitLab, Gitea, Bitbucket
or your own server) and keeps them up to date. A web interface shows what would change before anything is
pushed, which files the exclude rules keep out, and lets you adjust those rules with a click.

> **Beta.** Version 2 is a rewrite around the web interface. Updating from 1.x needs no action: the old
> repository moves into the new list by itself, and the architectures stay the same.

* **Preview instead of guessing.** A dry run lists every new, changed and removed file with its diff.
* **See what the rules do.** A browser for the whole file tree marks what is left out and by which rule.
* **Presets that fit a Home Assistant.** Databases, logs, caches, keys, credentials, large media and HACS
  downloads stay out; your own patterns, with a test, are added in the web interface and saved to the options.
* **Any number of repositories**, each with its own login, branch and message.
* **Public or private per repository.** For the public, `secrets.yaml` is emptied (even with `>-` template
  blocks and nested entries) and IP and MAC addresses, secret values and the like are censored. For private use
  everything is exported as it is, after the app has checked that the repository really is private and, if it is
  not, let you decide.
* Also exports `/local_apps` and `/app_configs` (both the new and the old folder names are found).

## Install

In Home Assistant open **Settings → Apps → App store → ⋮ → Repositories**, add
`https://github.com/seb5594/Home-Assistant-Apps` and install **Home Assistant Git Exporter**.
Older versions call these *Add-ons* and *Add-on store*. Setup, options and troubleshooting are in the
**[documentation](git-exporter/DOCS.md)**; the changes are in the **[changelog](git-exporter/CHANGELOG.md)**.

## Development

```text
git-exporter/
  config.yaml, translations/            options and their labels
  rootfs/opt/git-exporter/exporter/     the exporter (Python): rules, censoring, git, web API
  rootfs/opt/git-exporter/web/          the web interface (plain HTML, CSS and JavaScript)
  rootfs/etc/s6-overlay/                the service
.github/tests/                          unit tests, run inside the built image by runtime.sh
```

Based on the original Git Exporter work from the Home Assistant community. Maintained by
[seb5594](https://github.com/seb5594).

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
