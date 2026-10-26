"""The folders that are exported and the rules that decide which of their files are.

One folder is one Source. A Source has a root on disk, a folder name in the repository and a set of
rules: mandatory ones that nothing can lift, the presets, and the user's own patterns.
"""
import os
import time
from dataclasses import dataclass

from . import matcher, presets

# Mount points, newest name first. Home Assistant renamed the folders with the introduction of apps
# (/addon_configs became /app_configs, /addons became /local_apps); both are looked for.
ROOTS = {
    "config": ("/homeassistant", "/config"),
    "addon_configs": ("/app_configs", "/addon_configs"),
    "local_apps": ("/local_apps", "/addons", "/local_addons"),
}


@dataclass(frozen=True)
class Source:
    id: str
    dest: str
    root_kind: str
    title: dict
    subdir: str = ""
    # Files must match one of these to be exported (the folder is walked either way).
    allow: tuple = ()
    export_flag: str = ""

    def root(self):
        for candidate in ROOTS[self.root_kind]:
            path = os.path.join(candidate, self.subdir) if self.subdir else candidate
            if os.path.isdir(path):
                return path
        return None


SOURCES = (
    Source("config", "config", "config", {"en": "Home Assistant configuration", "de": "Home-Assistant-Konfiguration"}),
    Source("esphome", "esphome", "config", {"en": "ESPHome", "de": "ESPHome"}, subdir="esphome",
           allow=("*.yaml", "*.disabled", ".gitignore"), export_flag="esphome"),
    Source("node_red", "node-red", "config", {"en": "Node-RED", "de": "Node-RED"}, subdir="node-red",
           allow=("/flows.json", "/settings.js"), export_flag="node_red"),
    Source("local_apps", "local_apps", "local_apps", {"en": "Local apps", "de": "Lokale Apps"},
           export_flag="local_apps"),
    Source("addon_configs", "addons_config", "addon_configs", {"en": "App configurations", "de": "App-Konfigurationen"},
           export_flag="addon_configs"),
)
BY_ID = {source.id: source for source in SOURCES}
SECRETS_FILE = "secrets.yaml"


def active(settings):
    """The sources that are switched on and exist on this system."""
    return [source for source in SOURCES
            if (not source.export_flag or settings.export.get(source.export_flag)) and source.root()]


@dataclass(frozen=True)
class Decision:
    status: str          # included | excluded | too_large
    rule: str = ""
    origin: str = ""     # mandatory | separate | preset:<id> | custom | allow | size

    @property
    def excluded(self):
        return self.status != "included"


INCLUDED = Decision("included")


@dataclass
class Item:
    path: str
    is_dir: bool
    size: int
    decision: Decision
    mtime: float = 0.0


class Rules:
    """The rules of one source for one set of settings."""

    def __init__(self, source, settings):
        self.source = source
        self.settings = settings
        self.mandatory = matcher.Ruleset([(p, "mandatory") for p in presets.mandatory_for(source.id)])
        self.separate = matcher.Ruleset()
        if source.id == "config":
            separate = [(f"/{s.subdir}/", f"separate:{s.id}") for s in SOURCES if s.subdir]
            self.mandatory = matcher.Ruleset(
                [(p, "mandatory") for p in presets.mandatory_for(source.id) if not p.startswith(("/esphome", "/node-red"))])
            self.separate = matcher.Ruleset(separate)
        patterns = []
        for preset in presets.PRESETS:
            if (preset.sources is None or source.id in preset.sources) and presets.enabled(preset, settings.presets):
                patterns.extend((p, f"preset:{preset.id}") for p in preset.patterns)
        patterns.extend((p, "custom") for p in settings.exclude)
        self.rules = matcher.Ruleset(patterns)
        self.allow = matcher.Ruleset([(p, "allow") for p in source.allow]) if source.allow else None

    def decide(self, rel, is_dir, size=0, inherited=INCLUDED):
        hit = self.mandatory.match(rel, is_dir)
        if hit and hit[0]:
            return Decision("excluded", hit[1], "mandatory")
        hit = self.separate.match(rel, is_dir)
        if hit and hit[0]:
            return Decision("excluded", hit[1], hit[2])
        hit = self.rules.match(rel, is_dir)
        if hit:
            decision = Decision("excluded", hit[1], hit[2]) if hit[0] else INCLUDED
        else:
            decision = inherited
        if decision.excluded or is_dir:
            return decision
        if self.allow is not None and not self.allow.match(rel, False):
            return Decision("excluded", ", ".join(self.source.allow), "allow")
        if size > self.settings.max_file_size and rel != SECRETS_FILE:
            return Decision("too_large", f"> {self.settings.max_file_size_mb} MB", "size")
        return decision

    def inherited_for(self, rel):
        """The state of a folder's content: what the folder and its parents decide."""
        state = INCLUDED
        parts = rel.split("/") if rel else []
        for depth in range(1, len(parts) + 1):
            state = self.decide("/".join(parts[:depth]), True, 0, state)
        return state


def _scan(path):
    try:
        with os.scandir(path) as entries:
            return sorted(entries, key=lambda entry: entry.name)
    except OSError:
        return []


def list_dir(rules, rel=""):
    """One level of a folder, each entry with the decision the rules make about it."""
    root = rules.source.root()
    if root is None:
        return []
    folder = os.path.join(root, rel) if rel else root
    inherited = rules.inherited_for(rel)
    items = []
    for entry in _scan(folder):
        if entry.is_symlink():
            continue
        is_dir = entry.is_dir(follow_symlinks=False)
        try:
            stat = entry.stat(follow_symlinks=False)
        except OSError:
            continue
        path = f"{rel}/{entry.name}" if rel else entry.name
        size = 0 if is_dir else stat.st_size
        items.append(Item(path, is_dir, size, rules.decide(path, is_dir, size, inherited), stat.st_mtime))
    return items


def walk(rules, include_excluded=False):
    """Every file of a source that is exported (and, on request, those that are not, with the reason)."""
    root = rules.source.root()
    if root is None:
        return

    def visit(folder, rel, inherited):
        for entry in _scan(folder):
            if entry.is_symlink():
                continue
            is_dir = entry.is_dir(follow_symlinks=False)
            path = f"{rel}/{entry.name}" if rel else entry.name
            try:
                stat = entry.stat(follow_symlinks=False)
            except OSError:
                continue
            decision = rules.decide(path, is_dir, 0 if is_dir else stat.st_size, inherited)
            if is_dir:
                if decision.excluded and not rules.rules.has_negation:
                    if include_excluded:
                        yield Item(path, True, 0, decision, stat.st_mtime)
                    continue
                yield from visit(entry.path, path, decision)
            elif include_excluded or not decision.excluded:
                yield Item(path, False, stat.st_size, decision, stat.st_mtime)

    yield from visit(root, "", INCLUDED)


def directory_size(path, deadline=None):
    """(files, bytes) below a folder; stops early at `deadline` (a time.monotonic() value)."""
    files = total = 0
    stack = [path]
    while stack:
        if deadline is not None and time.monotonic() > deadline:
            return files, total
        for entry in _scan(stack.pop()):
            if entry.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                stack.append(entry.path)
            else:
                try:
                    total += entry.stat(follow_symlinks=False).st_size
                except OSError:
                    continue
                files += 1
    return files, total


def summarize(rules, seconds=20):
    """What the rules do to each top-level entry: files and bytes that stay and that are left out."""
    root = rules.source.root()
    deadline = time.monotonic() + seconds
    result = []
    complete = True
    for item in list_dir(rules):
        row = {"path": item.path, "dir": item.is_dir, "status": item.decision.status, "rule": item.decision.rule,
               "origin": item.decision.origin, "kept_files": 0, "kept_bytes": 0, "left_files": 0, "left_bytes": 0}
        if not item.is_dir:
            key = "kept" if not item.decision.excluded else "left"
            row[f"{key}_files"], row[f"{key}_bytes"] = 1, item.size
        elif item.decision.excluded and not rules.rules.has_negation:
            row["left_files"], row["left_bytes"] = directory_size(os.path.join(root, item.path), deadline)
        else:
            for found in walk_below(rules, item.path, item.decision):
                key = "left" if found.decision.excluded else "kept"
                row[f"{key}_files"] += 1
                row[f"{key}_bytes"] += found.size
        result.append(row)
        if time.monotonic() > deadline:
            complete = False
            break
    return {"entries": result, "complete": complete}


def walk_below(rules, rel, inherited):
    """Every file below a folder with its decision, excluded ones included."""
    root = rules.source.root()
    stack = [(os.path.join(root, rel), rel, inherited)]
    while stack:
        folder, folder_rel, state = stack.pop()
        for entry in _scan(folder):
            if entry.is_symlink():
                continue
            is_dir = entry.is_dir(follow_symlinks=False)
            path = f"{folder_rel}/{entry.name}"
            try:
                size = 0 if is_dir else entry.stat(follow_symlinks=False).st_size
            except OSError:
                continue
            decision = rules.decide(path, is_dir, size, state)
            if is_dir:
                stack.append((entry.path, path, decision))
            else:
                yield Item(path, False, size, decision)
