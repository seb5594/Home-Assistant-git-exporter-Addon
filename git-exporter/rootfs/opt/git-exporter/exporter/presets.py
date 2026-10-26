"""Exclude presets: ready-made groups of patterns for what does not belong into a git repository.

A preset is on unless the app options switch it off. The patterns use the notation of matcher.py.
The user's own patterns come after the presets, so a `!pattern` of theirs can keep something back.
"""
from dataclasses import dataclass

# Sources a preset applies to; None means all of them.
CONFIG = ("config",)
APP_CONFIGS = ("addon_configs",)


@dataclass(frozen=True)
class Preset:
    id: str
    patterns: tuple
    title: dict
    description: dict
    sources: tuple | None = None
    default: bool = True


PRESETS = (
    Preset(
        "databases",
        ("*.db", "*.db-shm", "*.db-wal", "*.db-journal", "*.sqlite", "*.sqlite3", "*.sqlite-shm", "*.sqlite-wal",
         "*.sql", "*.rdb", "*.mdb", "*.ldb"),
        {"en": "Databases", "de": "Datenbanken"},
        {"en": "SQLite and other database files, including the recorder database of Home Assistant. They are large, change all the time and hold your history.",
         "de": "SQLite- und andere Datenbankdateien, auch die Recorder-Datenbank von Home Assistant. Sie sind groß, ändern sich ständig und enthalten deinen Verlauf."},
    ),
    Preset(
        "logs",
        ("*.log", "*.log.*", "*.log[0-9]*", "*_log.txt", "*-log.txt", "OZW_Log.txt"),
        {"en": "Log files", "de": "Protokolldateien"},
        {"en": "Log files of Home Assistant and of other software.",
         "de": "Protokolldateien von Home Assistant und anderer Software."},
    ),
    Preset(
        "caches",
        ("__pycache__/", "*.pyc", "*.pyo", ".cache/", ".pytest_cache/", "deps/", "*.tmp", "*.swp", "*~",
         ".DS_Store", "._*", "Thumbs.db"),
        {"en": "Caches and temporary files", "de": "Caches und temporäre Dateien"},
        {"en": "Python caches, downloaded dependencies and the leftovers of editors and file managers.",
         "de": "Python-Caches, heruntergeladene Abhängigkeiten und Überbleibsel von Editoren und Dateimanagern."},
    ),
    Preset(
        "runtime_state",
        ("/.HA_VERSION", "/.ha_run.lock", "*.pid", "/known_devices.yaml", "/ip_bans.yaml", "/.google.token",
         "/zigbee.db*", "/.exports", "/.timeline", "/.vacuum"),
        {"en": "Runtime state of Home Assistant", "de": "Laufzeitzustand von Home Assistant"},
        {"en": "Lock files, the version marker, known devices and IP bans: written by Home Assistant while it runs, not configuration.",
         "de": "Sperrdateien, die Versionsmarke, bekannte Geräte und IP-Sperren: Home Assistant schreibt sie im Betrieb, es ist keine Konfiguration."},
        CONFIG,
    ),
    Preset(
        "generated_content",
        ("/tts/", "/image/", "/camera/", "/snapshots/"),
        {"en": "Generated content", "de": "Erzeugte Inhalte"},
        {"en": "Text-to-speech audio, uploaded images and camera snapshots.",
         "de": "Sprachausgabe-Audio, hochgeladene Bilder und Kamera-Schnappschüsse."},
        CONFIG,
    ),
    Preset(
        "credentials",
        ("secrets.env", ".env", "*.env", ".env.*", "credentials", "credentials.*", "*.credentials", "client_secret*.json", "*.token", "*_token", ".netrc", ".npmrc",
         ".pypirc", ".git-credentials", ".htpasswd", ".ssh/", ".gnupg/", "*.kdbx", "*.keystore", "*.jks",
         "*.ovpn", "*.psk", "auth.json"),
        {"en": "Credentials", "de": "Zugangsdaten"},
        {"en": "Environment files, token files, password stores and VPN profiles. They hold passwords by design.",
         "de": "Umgebungsdateien, Token-Dateien, Passwortspeicher und VPN-Profile. Sie enthalten von Natur aus Passwörter."},
    ),
    Preset(
        "keys_certificates",
        ("*.key", "*.pem", "*.crt", "*.cer", "*.csr", "*.p12", "*.pfx", "*.der", "*.ppk", "id_rsa*", "id_ed25519*",
         "id_ecdsa*", "known_hosts", "authorized_keys", "*.gpg"),
        {"en": "Keys and certificates", "de": "Schlüssel und Zertifikate"},
        {"en": "Private keys and certificates, such as those of a reverse proxy or a web server app.",
         "de": "Private Schlüssel und Zertifikate, zum Beispiel die eines Reverse-Proxys oder einer Webserver-App."},
    ),
    Preset(
        "media",
        ("*.mp3", "*.wav", "*.flac", "*.ogg", "*.m4a", "*.aac", "*.mp4", "*.mkv", "*.avi", "*.mov", "*.webm", "*.iso"),
        {"en": "Audio and video", "de": "Audio und Video"},
        {"en": "Audio and video files: large, and not configuration.",
         "de": "Audio- und Videodateien: groß und keine Konfiguration."},
    ),
    Preset(
        "archives",
        ("*.zip", "*.tar", "*.tar.*", "*.tgz", "*.gz", "*.bz2", "*.xz", "*.7z", "*.rar"),
        {"en": "Archives", "de": "Archive"},
        {"en": "Zip and tar archives, including compressed backups.",
         "de": "Zip- und Tar-Archive, auch komprimierte Sicherungen."},
    ),
    Preset(
        "backup_copies",
        ("*.bak", "*.backup", "*.backup[0-9]*", "*.old", "*.old.*", "*.oldx[0-9]*", "*.orig", "backups/"),
        {"en": "Copies and old versions", "de": "Kopien und alte Versionen"},
        {"en": "Files and folders named .bak, .backup, .old or .orig: copies of something that is already exported.",
         "de": "Dateien und Ordner mit .bak, .backup, .old oder .orig im Namen: Kopien von etwas, das schon exportiert wird."},
    ),
    Preset(
        "hacs_downloads",
        ("/custom_components/", "/www/community/", "/www/hacsfiles/", "/hacs/"),
        {"en": "Custom integrations and cards", "de": "Eigene Integrationen und Karten"},
        {"en": "What HACS and other stores download: it can be installed again. To keep one of your own integrations, add a pattern such as !/custom_components/my_integration in the list below (and exclude the rest with /custom_components/*).",
         "de": "Was HACS und andere Stores herunterladen: es lässt sich neu installieren. Um eine eigene Integration zu behalten, trage unten ein Muster wie !/custom_components/meine_integration ein (und schließe den Rest mit /custom_components/* aus)."},
        CONFIG,
    ),
    Preset(
        "development",
        ("node_modules/", ".venv/", "venv/", ".ipynb_checkpoints/", "/notebooks/", ".idea/", ".vscode/", "*.egg-info/"),
        {"en": "Development leftovers", "de": "Entwicklungsreste"},
        {"en": "Notebooks, virtual environments and editor folders.",
         "de": "Notebooks, virtuelle Umgebungen und Editor-Ordner."},
    ),
    Preset(
        "app_runtime_data",
        ("*/db/", "*/data/", "*/cache/", "*/caches/", "*/logs/", "*/log/", "*/uploads/", "*/ssl/", "*/certs/",
         "*/certificates/", "*/backup/", "*/tmp/", "*/temp/"),
        {"en": "Runtime data of apps", "de": "Laufzeitdaten von Apps"},
        {"en": "The folders in which apps keep their databases, uploads, caches, logs and certificates.",
         "de": "Die Ordner, in denen Apps ihre Datenbanken, Uploads, Caches, Protokolle und Zertifikate ablegen."},
        APP_CONFIGS,
    ),
)

BY_ID = {preset.id: preset for preset in PRESETS}

# What is never exported, whatever the settings say: Home Assistant's own state holds access
# tokens, and a nested git repository would make the export a mess.
MANDATORY = {
    None: (".git/",),
    "config": ("/.storage/", "/.cloud/", "/.uuid", "/home-assistant_v2.db*", "/esphome/", "/node-red/"),
}


def enabled(preset, switches):
    """Whether a preset is on; `switches` is the presets group of the options."""
    value = (switches or {}).get(preset.id)
    return preset.default if value is None else bool(value)


def patterns_for(source_id, switches, custom):
    """The patterns for one source, in the order they are applied: presets, then the user's."""
    patterns = []
    for preset in PRESETS:
        if (preset.sources is None or source_id in preset.sources) and enabled(preset, switches):
            patterns.extend(preset.patterns)
    patterns.extend(custom)
    return patterns


def mandatory_for(source_id):
    return MANDATORY[None] + MANDATORY.get(source_id, ())
