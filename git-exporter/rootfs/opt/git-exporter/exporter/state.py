"""What the app remembers between runs, in /data/state.json: the last result of each repository and
the decisions of the user (a public remote they accepted for a private repository)."""
import json
import os
import threading
import time

from .gitops import DATA_DIR

_LOCK = threading.Lock()


def _path():
    return DATA_DIR / "state.json"


def _read():
    try:
        with open(_path(), encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def _write(data):
    _path().parent.mkdir(parents=True, exist_ok=True)
    temporary = _path().with_suffix(".tmp")
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=1)
    os.replace(temporary, _path())


def get(slug):
    with _LOCK:
        return dict(_read().get("repositories", {}).get(slug, {}))


def update(slug, **values):
    with _LOCK:
        data = _read()
        entry = data.setdefault("repositories", {}).setdefault(slug, {})
        entry.update(values)
        _write(data)


def acknowledge_public_remote(slug, url):
    update(slug, accepted_public_remote={"url": url, "at": time.strftime("%Y-%m-%d %H:%M:%S")})


def public_remote_accepted(slug, url):
    return get(slug).get("accepted_public_remote", {}).get("url") == url


def forget_public_remote(slug):
    update(slug, accepted_public_remote=None)
