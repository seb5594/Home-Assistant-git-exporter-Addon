"""Shared setup for the tests: where the exporter package is, and a small Home Assistant to export."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1] if len(HERE.parents) > 1 else HERE
CANDIDATES = (os.environ.get("EXPORTER_PATH"), "/opt/git-exporter", str(REPOSITORY / "git-exporter/rootfs/opt/git-exporter"))
WEB_DIR = next((Path(c) / "web" for c in CANDIDATES if c and (Path(c) / "web/index.html").is_file()), None)
for candidate in CANDIDATES:
    if candidate and (Path(candidate) / "exporter").is_dir():
        sys.path.insert(0, candidate)
        break

from exporter import gitops, options, sources  # noqa: E402

SECRETS = """\
#################################################################
#                            Secrets                            #
#################################################################
# Use this file to store secrets like usernames and passwords.

server_friendly_name: Sebis Zuhause
ip_router: 192.168.178.1
mac_desktop: "AA:BB:CC:11:22:33"   # desktop

template_home_presence: >-
  {% set users = states
     | selectattr('domain', 'eq', 'person')
     | selectattr('state', 'eq', 'home')
     | map(attribute='attributes.friendly_name')
     | list
   %}
  {% set distances = [
      ('sensor.zuhause_sebastian_entfernung', 150),
      ('sensor.zuhause_2_alfi_entfernung', 150)
    ] %}
  {% if users | select('is_state','home') | list | count > 0 %}
    on
  {% elif distances | selectattr(0,'defined') | selectattr(0,'states') 
         | map('int') | select('<', 150) | list | count > 0 %}
    on
  {% else %}
    off
  {% endif %}

# whatsapp nummern
whatsapp_phonebook:
  sebi: 491701234567
  alfi: 491709876543
  kosti: 491705551234
  rfx: 491706667777

api_key_weather: abcdef1234567890abcdef
"""

CONFIGURATION = """\
homeassistant:
  name: !secret server_friendly_name
  latitude: 52.52
http:
  trusted_proxies:
    - 192.168.178.1
device_tracker:
  - host: 192.168.178.1
    mac: AA:BB:CC:11:22:33
    password: hunter2hunter2
sensor: !include sensors.yaml
"""


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                        "GIT_COMMITTER_EMAIL": "t@t"})


class World:
    """A temporary /config, /addon_configs and /data, and a bare git repository to push to."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.config, self.app_configs, self.data, self.remote = (base / n for n in ("config", "app_configs", "data", "remote.git"))
        for folder in (self.config, self.app_configs, self.data):
            folder.mkdir()
        git("init", "-q", "--bare", "-b", "main", str(self.remote), cwd=base)
        (self.config / "secrets.yaml").write_text(SECRETS)
        (self.config / "configuration.yaml").write_text(CONFIGURATION)
        (self.config / "automations.yaml").write_text("- alias: test\n")
        (self.config / "home-assistant.log").write_text("log")
        (self.config / "home-assistant_v2.db").write_bytes(b"\0" * 100)
        (self.config / ".storage").mkdir()
        (self.config / ".storage/auth").write_text('{"token": "x"}')
        (self.config / "custom_components/foo").mkdir(parents=True)
        (self.config / "custom_components/foo/__init__.py").write_text("x = 1\n")
        (self.config / "www").mkdir()
        (self.config / "www/big.png").write_bytes(b"\x89PNG" + b"\0" * (6 * 1024 * 1024))
        (self.config / "esphome").mkdir()
        (self.config / "esphome/node.yaml").write_text("esphome:\n  name: node\n")
        (self.config / "esphome/build.bin").write_bytes(b"\0")
        (self.app_configs / "abc_gitea").mkdir()
        (self.app_configs / "abc_gitea/app.ini").write_text("[server]\nHTTP_ADDR = 10.0.0.5\n")
        (self.app_configs / "abc_gitea/data").mkdir()
        (self.app_configs / "abc_gitea/data/gitea.db").write_bytes(b"\0")
        sources.ROOTS["config"] = (str(self.config),)
        sources.ROOTS["addon_configs"] = (str(self.app_configs),)
        sources.ROOTS["local_apps"] = (str(base / "nothing"),)
        gitops.DATA_DIR = self.data

    def settings(self, audience="public", **overrides):
        raw = {"repositories": [{"name": "Main", "url": str(self.remote), "audience": audience, "check_visibility": False}],
               "export": {"lovelace": False, "addons": False}}
        raw.update(overrides)
        return options.parse(raw)

    def close(self):
        self.tmp.cleanup()
