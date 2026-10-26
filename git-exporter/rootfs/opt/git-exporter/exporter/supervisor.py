"""The parts of the Supervisor API this app uses."""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("SUPERVISOR_URL", "http://supervisor")


class SupervisorError(Exception):
    pass


def _token():
    return os.environ.get("SUPERVISOR_TOKEN", "")


def request(method, path, body=None, timeout=20):
    """The `data` of a Supervisor reply; a failed call raises SupervisorError with the Supervisor's message."""
    data = json.dumps(body).encode() if body is not None else None
    call = urllib.request.Request(f"{BASE}{path}", data=data, method=method,
                                  headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(call, timeout=timeout) as reply:
            payload = json.load(reply)
    except urllib.error.HTTPError as error:
        try:
            message = json.load(error).get("message", "")
        except (ValueError, OSError):
            message = ""
        raise SupervisorError(message or f"HTTP {error.code} for {path}") from error
    except (urllib.error.URLError, OSError, ValueError) as error:
        raise SupervisorError(f"The Supervisor does not answer ({error})") from error
    if payload.get("result") == "error":
        raise SupervisorError(payload.get("message") or f"The Supervisor refused {path}")
    return payload.get("data")


def available():
    return bool(_token())


def self_info():
    return request("GET", "/addons/self/info")


def current_options():
    """The options as stored right now, which may be newer than /data/options.json."""
    return self_info().get("options") or {}


def save_options(options):
    """Validates and stores the options of this app."""
    check = request("POST", "/addons/self/options/validate", {"options": options})
    if isinstance(check, dict) and check.get("valid") is False:
        raise SupervisorError(check.get("message") or "The options are not valid")
    request("POST", "/addons/self/options", {"options": options})


def stop_self():
    request("POST", "/addons/self/stop", timeout=30)


def installed_apps():
    data = request("GET", "/addons")
    return [entry["slug"] for entry in (data or {}).get("addons", [])]


def app_info(slug):
    return request("GET", f"/addons/{slug}/info")


def store_repositories():
    return request("GET", "/store/repositories") or []
