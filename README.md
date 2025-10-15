# Home Assistant Git Exporter

Export all of your Home Assistant configuration to a git repository of your choice.  
Can be used to show your Home Assistant setup in public repositories.

![Addon Stage][stage-badge]
![Supports aarch64 Architecture][aarch64-badge]
![Supports amd64 Architecture][amd64-badge]
![Supports armhf Architecture][armhf-badge]
![Supports armv7 Architecture][armv7-badge]
![Supports i386 Architecture][i386-badge]

[![Add repository on my Home Assistant][repository-badge]][repository-url]
[![Install on my Home Assistant][install-badge]][install-url]
[![Donate][donation-badge]][donation-url]

This add-on has been **improved** with the following updates:

> - ✅ Fully respects **exclude rules** and removes unwanted files from the repository.  
> - ✅ Proper export of **add-on configs** from `/addon_configs`.  
> - ✅ **Commit messages** now support a `{DATE}` placeholder for automatic timestamping.  
> - ✅ Only **shell scripts are executable**; all other files have **normalized permissions**.  
> - ✅ Optional **secret and IP checks** to prevent sensitive data from being committed.  
> - ✅ Add-on **stops automatically** after a successful export, reducing manual intervention.


# Functionality

* Export Home Assistant configuration.
* Export Supervisor Addon configuration.
* Export Lovelace configuration.
* Export ESPHome configurations.
* Export Node-RED flows.
* Check for plaintext secrets based on your `secrets.yaml` file and common patterns.
* Check for plaintext ip and addresses in your config.

# Example

For an example take a look at my own [Home Assistant configuration](https://github.com/Poeschl/home-assistant-config).  
The folders there are getting synced with this addon.

# Badge

If you export your config with this addon and want to help me to spread it further, here is a badge you can embed in your README.

[![Home Assistant Git Exporter](https://img.shields.io/badge/Powered%20by-Home%20Assistant%20Git%20Exporter-%23d32f2f)]([https://github.com/seb5594/Home-Assistant-git-exporter-Addon/tree/main/git-exporter](https://github.com/seb5594/Home-Assistant-git-exporter-Addon/git-exporter)

```markdown
[![Home Assistant Git Exporter](https://img.shields.io/badge/Powered%20by-Home%20Assistant%20Git%20Exporter-%23d32f2f)](https://github.com/Poeschl/Hassio-Addons/tree/main/git-exporter)
