"""Exclude patterns in the notation of a .gitignore file.

    *.db            a name at any depth
    deps/           a folder (and everything in it) at any depth
    /tts/           anchored to the root of the exported folder
    custom_components/foo   a path: anchored as well, because it contains a slash
    **/cache/*.tmp  `**` crosses folders, `*` and `?` do not
    !keep_me.yaml   keep what an earlier pattern excluded; the last matching pattern wins

Blank lines and lines starting with # are ignored. Patterns of the older rsync based exporter
(`*.log*`, `__pycache__`, `deps/`) mean the same here.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    text: str
    negated: bool
    directory_only: bool
    anchored: bool
    regex: re.Pattern
    origin: str = ""

    def matches(self, path, name, is_dir):
        if self.directory_only and not is_dir:
            return False
        return bool(self.regex.fullmatch(path if self.anchored else name))


def _translate(glob):
    """A glob without slashes at its ends as a regular expression."""
    out, i = [], 0
    while i < len(glob):
        char = glob[i]
        if glob.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
            continue
        if glob.startswith("/**", i) and i + 3 == len(glob):
            out.append("/.*")
            i += 3
            continue
        if glob.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        if char == "*":
            out.append("[^/]*")
        elif char == "?":
            out.append("[^/]")
        elif char == "[":
            end = glob.find("]", i + 2)
            if end == -1:
                out.append(re.escape(char))
            else:
                body = glob[i + 1:end]
                if body.startswith("!"):
                    body = "^" + body[1:]
                out.append("[" + body.replace("\\", "\\\\") + "]")
                i = end
        else:
            out.append(re.escape(char))
        i += 1
    return "".join(out)


def parse(line, origin=""):
    """One pattern as a Rule; None for a blank line or a comment. `origin` says where it came from."""
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    negated = text.startswith("!")
    glob = text[1:] if negated else text
    directory_only = glob.endswith("/")
    glob = glob.rstrip("/")
    anchored = glob.startswith("/") or "/" in glob
    glob = glob.lstrip("/")
    if not glob:
        return None
    return Rule(text, negated, directory_only, anchored, re.compile(_translate(glob)), origin)


class Ruleset:
    """An ordered list of patterns; decide() says what happens to one path."""

    def __init__(self, patterns=()):
        """`patterns` are strings or (string, origin) pairs."""
        parsed = (parse(*(item if isinstance(item, tuple) else (item,))) for item in patterns)
        self.rules = [rule for rule in parsed if rule]
        self.has_negation = any(rule.negated for rule in self.rules)

    def match(self, path, is_dir):
        """(excluded, pattern, origin) of the last pattern that matches, or None when none does."""
        name = path.rsplit("/", 1)[-1]
        verdict = None
        for rule in self.rules:
            if rule.matches(path, name, is_dir):
                verdict = (not rule.negated, rule.text, rule.origin)
        return verdict


def check(pattern):
    """None when the pattern is usable, otherwise a short reason."""
    text = pattern.strip()
    if not text or text.startswith("#"):
        return "empty"
    if text in ("!", "/", "*/", "**"):
        return "matches everything or nothing"
    try:
        parse(text)
    except re.error as error:
        return f"not a valid pattern ({error})"
    return None
