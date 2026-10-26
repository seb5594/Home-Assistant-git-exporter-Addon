"""Keeps private data out of a repository that is meant for the public.

The exporter hands every text file to `Censor.apply` before it is written into such a repository.
What is found is replaced and counted, never left in place:

* the values of secrets.yaml (found with a real YAML parser, so block scalars, nested mappings and
  comments are no problem) and any extra secrets from the options,
* IPv4, IPv6 and MAC addresses (replaced by the documentation ranges, the same address always by the
  same placeholder, so that the files still show which entries belong together),
* values of keys that are named like a secret (password, token, api_key, latitude, ...),
* passwords inside URLs and e-mail addresses.

`blank_secrets_yaml` writes the secrets.yaml of a public repository: the same keys and comments with
empty values.
"""
import hashlib
import ipaddress
import re
from collections import Counter
from dataclasses import dataclass

import yaml

CENSORED = "<censored>"
MIN_SECRET_LENGTH = 5
MAX_SECRETS = 5000
# Values that are words rather than secrets; a file that says "metric" has not leaked anything.
HARMLESS_VALUES = frozenset({
    "true", "false", "none", "null", "yes", "no", "on", "off", "metric", "imperial", "celsius", "fahrenheit",
    "localhost", "default", "home", "admin", "unknown",
})
# Public addresses that identify a service, not a household.
ALLOWED_ADDRESSES = frozenset({
    "1.1.1.1", "1.0.0.1", "8.8.8.8", "8.8.4.4", "9.9.9.9", "149.112.112.112", "208.67.222.222", "208.67.220.220",
    "0.0.0.0", "127.0.0.1", "255.255.255.255",
})
DOCUMENTATION_NETWORKS = tuple(ipaddress.ip_network(net) for net in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
PLACEHOLDER_POOL = [str(host) for net in DOCUMENTATION_NETWORKS for host in net.hosts()]

SENSITIVE_KEY = (
    r"password|passwd|pwd|passphrase|token|secret|api[_-]?key|apikey|client[_-]?id|chat[_-]?id|allowed_chat_ids|"
    r"latitude|longitude|private[_-]?key|access[_-]?key|webhook[_-]?id|encryption[_-]?key|credential[_-]?secret|"
    r"psk|bearer|session[_-]?id|auth[_-]?key|serial[_-]?number"
)
YAML_PAIR = re.compile(
    rf"""^(?P<head>[ \t]*(?:-[ \t]+)?(?P<key>["']?[\w.-]*(?:{SENSITIVE_KEY})[\w.-]*["']?)[ \t]*:[ \t]+)"""
    r"""(?P<value>[^\s#][^#\n]*?)(?P<tail>[ \t]+#.*)?$""",
    re.IGNORECASE | re.MULTILINE,
)
JSON_PAIR = re.compile(
    rf"""(?P<head>["']?[\w.-]*(?:{SENSITIVE_KEY})[\w.-]*["']?\s*:\s*)(?P<quote>["'])(?P<value>[^"'\n]+)(?P=quote)""",
    re.IGNORECASE,
)
COORDINATE_KEY = re.compile(r"latitude|longitude", re.IGNORECASE)
KEEP_VALUE = re.compile(r"""^(?:!|\{\{|\{%|\$\{|"?\{\{|['"]?!)""")
URL_CREDENTIALS = re.compile(r"(?P<scheme>\b[a-z][a-z0-9+.-]*://)(?P<user>[^/\s:@'\"]+):(?P<password>[^/\s@'\"]+)@")
EMAIL = re.compile(r"(?<![\w.+-])[A-Za-z0-9][A-Za-z0-9._%+-]*@(?P<domain>[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})\b")
PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
IPV4 = re.compile(
    r"(?<![\w.:-])((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})(?![\w-]|\.\d|\.[A-Za-z])")
MAC = re.compile(
    r"(?<![0-9A-Fa-f:.-])[0-9A-Fa-f]{2}([:-])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}(?![0-9A-Fa-f:.-])")
IPV6 = re.compile(
    r"(?<![\w:.])(?:(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|"
    r"(?:[0-9A-Fa-f]{1,4}:){1,6}(?::[0-9A-Fa-f]{1,4}){1,6}|"
    r"(?:[0-9A-Fa-f]{1,4}:){1,7}:|:(?::[0-9A-Fa-f]{1,4}){1,7})(?![\w:])")
# Four numbers that follow "version:" or "rev =" are a version, not an address.
VERSION_CONTEXT = re.compile(r"""(?:version|ver|rev|release|build)[\w\s"'-]*[:=]\s*["']?[vV]?$""", re.IGNORECASE)
TEMPLATE_ONLY = re.compile(r"^[\s{}%#|>\-]*(?:end\w*|else|elif|if|for|set|macro|endmacro)?[\s{}%#|>\-]*$")


class _TolerantLoader(yaml.SafeLoader):
    """Reads secrets.yaml including tags such as !env_var or !include as plain values."""


_TolerantLoader.add_multi_constructor(
    "!", lambda loader, suffix, node: loader.construct_scalar(node) if isinstance(node, yaml.ScalarNode) else None)


@dataclass(frozen=True)
class Secret:
    key: str
    value: str
    top_level: bool


def _flatten(node, path, top_level, out):
    if isinstance(node, dict):
        for key, value in node.items():
            _flatten(value, f"{path}.{key}" if path else str(key), top_level and not path, out)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _flatten(value, f"{path}[{index}]", False, out)
    elif node is not None and not isinstance(node, bool):
        out.append(Secret(path, str(node), top_level and "." not in path and "[" not in path))


def _fallback_pairs(text):
    """secrets.yaml that is not valid YAML: every `key: value` line still gives a value."""
    found = []
    for line in text.splitlines():
        match = re.match(r"^\s*(?:-\s+)?([\w.-]+)\s*:\s+(\S.*?)\s*$", line)
        if match and not match.group(2).startswith(("#", ">", "|")):
            found.append(Secret(match.group(1), match.group(2).strip("'\""), True))
    return found


def parse_secrets(text):
    """The values stored in a secrets.yaml, with their key. Returns (secrets, parse_error or None)."""
    error = None
    try:
        data = yaml.load(text, Loader=_TolerantLoader)  # noqa: S506 - a SafeLoader subclass
        flat = []
        _flatten(data, "", True, flat)
    except yaml.YAMLError as problem:
        error = str(problem).splitlines()[0]
        flat = _fallback_pairs(text)
    return flat, error


def secret_candidates(secrets):
    """What to look for in files: (needle, secret). Multi-line values are searched whole and by line."""
    candidates = {}
    for secret in secrets:
        value = secret.value.strip()
        if "\n" in value:
            candidates.setdefault(value, secret)
            candidates.setdefault(" ".join(value.split()), secret)
            for line in value.splitlines():
                line = line.strip()
                if len(line) >= 20 and not TEMPLATE_ONLY.match(line):
                    candidates.setdefault(line, secret)
        else:
            candidates.setdefault(value, secret)
    usable = {needle: secret for needle, secret in candidates.items()
              if len(needle) >= MIN_SECRET_LENGTH and needle.lower() not in HARMLESS_VALUES
              and not (needle.isdigit() and len(needle) < 6)}
    ranked = sorted(usable, key=len, reverse=True)[:MAX_SECRETS]
    return [(needle, usable[needle]) for needle in ranked]


def _word_edges(needle):
    left = r"(?<![A-Za-z0-9_])" if needle[0].isalnum() or needle[0] == "_" else ""
    right = r"(?![A-Za-z0-9_])" if needle[-1].isalnum() or needle[-1] == "_" else ""
    return left, right


def placeholder_address(address):
    """The documentation address that stands for `address`; the same one every time."""
    digest = int(hashlib.sha256(address.encode()).hexdigest(), 16)
    return PLACEHOLDER_POOL[digest % len(PLACEHOLDER_POOL)]


def placeholder_mac(mac, separator):
    digest = hashlib.sha256(mac.lower().encode()).digest()
    parts = ["00", "00", "5E", "00", "53", f"{digest[0]:02X}"]
    return separator.join(parts)


def placeholder_ipv6(address):
    digest = hashlib.sha256(address.lower().encode()).hexdigest()
    return f"2001:db8::{digest[:4]}"


def _is_netmask(address):
    octets = [int(part) for part in address.split(".")]
    bits = "".join(f"{octet:08b}" for octet in octets)
    return re.fullmatch(r"1*0*", bits) is not None


def is_private_ipv4(address):
    """True for an address worth hiding: not a netmask, a documentation address or a well-known service."""
    if address in ALLOWED_ADDRESSES or _is_netmask(address):
        return False
    return not any(ipaddress.ip_address(address) in net for net in DOCUMENTATION_NETWORKS)


def looks_like_text(data):
    """False for binary content: a NUL byte or something that is not UTF-8."""
    if b"\x00" in data[:8192]:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


@dataclass
class Result:
    text: str
    findings: Counter
    blocked: str | None = None


class Censor:
    """Replaces private data in text. One instance serves a whole export."""

    def __init__(self, secrets=(), extra_secrets=(), allowed=(), check_secrets=True, check_addresses=True):
        self.check_secrets = check_secrets
        self.check_addresses = check_addresses
        self.allowed = tuple(item for item in allowed if item)
        extra = [Secret("(options)", value, False) for value in extra_secrets if value]
        self.candidates = secret_candidates(list(secrets) + extra) if check_secrets else []
        self.by_needle = dict(self.candidates)
        self.pattern = None
        if self.candidates:
            alternatives = []
            for needle, _ in self.candidates:
                left, right = _word_edges(needle)
                alternatives.append(f"{left}{re.escape(needle)}{right}")
            self.pattern = re.compile("|".join(alternatives))

    # -- helpers -----------------------------------------------------------------------------

    def _allowed(self, text):
        return any(item in text for item in self.allowed)

    def _count(self, findings, category, amount=1):
        findings[category] += amount

    # -- the passes --------------------------------------------------------------------------

    def _whole_values(self, text, findings):
        """`key: <secret>` in a YAML file becomes `key: !secret <name>` when the secret is a top-level key."""
        def swap(match):
            value = match.group("value").strip()
            plain = value[1:-1] if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"" else value
            secret = self.by_needle.get(plain)
            if secret is None or not secret.top_level or self._allowed(plain):
                return match.group(0)
            self._count(findings, "secret values")
            return f"{match.group('head')}!secret {secret.key}{match.group('tail') or ''}"
        return re.sub(r"^(?P<head>[ \t]*(?:-[ \t]+)?(?:[^\s:#][^:#\n]*:[ \t]+)?)(?P<value>[^\s#!{\[][^#\n]*?)(?P<tail>[ \t]+#.*)?$",
                      swap, text, flags=re.MULTILINE)

    def _secret_values(self, text, findings):
        def swap(match):
            if self._allowed(match.group(0)):
                return match.group(0)
            self._count(findings, "secret values")
            return CENSORED
        return self.pattern.sub(swap, text)

    def _keyed_values(self, text, findings):
        def yaml_value(match):
            value = match.group("value").strip()
            if KEEP_VALUE.match(value) or value in ("", "''", '""', "null", "~") or self._allowed(value):
                return match.group(0)
            self._count(findings, "values of secret-like keys")
            if COORDINATE_KEY.search(match.group("key")):
                replacement = "0.0"
            else:
                replacement = f'"{CENSORED}"'
            return f"{match.group('head')}{replacement}{match.group('tail') or ''}"

        def json_value(match):
            value = match.group("value")
            if value == CENSORED or self._allowed(value) or KEEP_VALUE.match(value):
                return match.group(0)
            self._count(findings, "values of secret-like keys")
            return f"{match.group('head')}{match.group('quote')}{CENSORED}{match.group('quote')}"

        return JSON_PAIR.sub(json_value, YAML_PAIR.sub(yaml_value, text))

    def _urls_and_mails(self, text, findings):
        def url(match):
            if self._allowed(match.group(0)) or match.group("password") in (CENSORED, "<password>"):
                return match.group(0)
            self._count(findings, "passwords in URLs")
            return f"{match.group('scheme')}{match.group('user')}:{CENSORED}@"

        def mail(match):
            if match.group("domain").lower().endswith(("example.com", "example.org", "example.net")) or self._allowed(match.group(0)):
                return match.group(0)
            self._count(findings, "e-mail addresses")
            return "user@example.com"

        return EMAIL.sub(mail, URL_CREDENTIALS.sub(url, text))

    def _addresses(self, text, findings):
        def mac(match):
            if self._allowed(match.group(0)):
                return match.group(0)
            self._count(findings, "MAC addresses")
            return placeholder_mac(match.group(0), match.group(1))

        def ipv4(match):
            address = match.group(1)
            if not is_private_ipv4(address) or self._allowed(address):
                return match.group(0)
            line_start = text.rfind("\n", 0, match.start()) + 1
            if VERSION_CONTEXT.search(text[line_start:match.start()]):
                return match.group(0)
            self._count(findings, "IP addresses")
            return placeholder_address(address)

        def ipv6(match):
            address = match.group(0)
            try:
                parsed = ipaddress.IPv6Address(address)
            except ValueError:
                return address
            if parsed.is_loopback or parsed.is_unspecified or self._allowed(address) or address.lower().startswith("2001:db8:"):
                return address
            self._count(findings, "IP addresses")
            return placeholder_ipv6(address)

        return IPV6.sub(ipv6, IPV4.sub(ipv4, MAC.sub(mac, text)))

    # -- entry point -------------------------------------------------------------------------

    def apply(self, text, name="", yaml_file=False):
        """The censored text, what was found, and a reason when the file must not be exported at all."""
        findings = Counter()
        if PRIVATE_KEY.search(text):
            return Result(text, findings, "contains a private key")
        if self.check_secrets:
            if self.pattern is not None:
                if yaml_file:
                    text = self._whole_values(text, findings)
                text = self._secret_values(text, findings)
            text = self._keyed_values(text, findings)
            text = self._urls_and_mails(text, findings)
        if self.check_addresses:
            text = self._addresses(text, findings)
        return Result(text, findings)


# ---- secrets.yaml of a public repository ----------------------------------------------------

_ENTRY = re.compile(
    r"""^(?P<indent>[ \t]*)(?P<dash>(?:-[ \t]+)*)(?P<key>"[^"]*"|'[^']*'|[^\s"'#\-][^:#]*?|-[^\s:#][^:#]*?)[ \t]*:(?P<rest>(?:[ \t]+.*)?)$""")
_ITEM = re.compile(r"^(?P<indent>[ \t]*)-[ \t]+(?P<rest>\S.*)$")


def _indent(line):
    return len(line) - len(line.lstrip(" \t"))


def _blank_lines(text):
    out, skip_deeper_than, pending_blanks = [], None, []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        newline = line[len(body):]
        stripped = body.strip()
        if skip_deeper_than is not None:
            # The lines below a block scalar or a value that continues on the next lines belong to it.
            if not stripped:
                pending_blanks.append(line)
                continue
            if _indent(body) > skip_deeper_than:
                pending_blanks.clear()
                continue
            skip_deeper_than = None
            out.extend(pending_blanks)
            pending_blanks.clear()
        if not stripped or stripped.startswith("#") or stripped in ("---", "..."):
            out.append(line)
            continue
        entry = _ENTRY.match(body)
        if entry:
            value = entry.group("rest").strip()
            if value == "" or value.startswith("#"):
                out.append(line)
                continue
            out.append(f'{entry.group("indent")}{entry.group("dash")}{entry.group("key")}: ""{newline}')
            skip_deeper_than = _indent(body)
            continue
        item = _ITEM.match(body)
        if item:
            out.append(f'{item.group("indent")}- ""{newline}')
            skip_deeper_than = _indent(body)
            continue
        out.append(line)
    out.extend(pending_blanks)
    return "".join(out)


def _skeleton(node):
    if isinstance(node, dict):
        return {key: _skeleton(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_skeleton(value) for value in node]
    return ""


def _shape(node):
    if isinstance(node, dict):
        return {key: _shape(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_shape(value) for value in node]
    return None


def blank_secrets_yaml(text):
    """secrets.yaml with every value emptied; keys, structure and comments stay.

    The result is checked against the original with a YAML parser. Should the line based pass ever
    get a file wrong, a plainly dumped skeleton of the same keys is returned instead.
    """
    blanked = _blank_lines(text)
    try:
        original = yaml.load(text, Loader=_TolerantLoader)  # noqa: S506
    except yaml.YAMLError:
        return blanked
    try:
        result = yaml.load(blanked, Loader=_TolerantLoader)  # noqa: S506
        if _shape(result) == _shape(_skeleton(original)):
            return blanked
    except yaml.YAMLError:
        pass
    return yaml.safe_dump(_skeleton(original), default_flow_style=False, allow_unicode=True)
