"""Log lines to stdout (the app log of Home Assistant) and to a short in-memory history for the web interface."""
import collections
import sys
import threading
import time

_LINES = collections.deque(maxlen=300)
_LOCK = threading.Lock()


def _write(level, message):
    stamp = time.strftime("%H:%M:%S")
    with _LOCK:
        _LINES.append({"time": stamp, "level": level, "message": message})
    print(f"[{stamp}] {level}: {message}", file=sys.stdout, flush=True)


def info(message):
    _write("INFO", message)


def warning(message):
    _write("WARNING", message)


def error(message):
    _write("ERROR", message)


def recent():
    with _LOCK:
        return list(_LINES)
