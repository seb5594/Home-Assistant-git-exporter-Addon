'use strict';

// ---- texts: English and German; the page follows the language of the browser -----------------
const TEXT = {
  en: {
    tab_overview: 'Overview', tab_preview: 'Preview', tab_files: 'Files', tab_excludes: 'Excludes', tab_checks: 'Checks',
    tab_log: 'Log',
    release: 'Pre-release {0}', busy: 'Working: {0}',
    repositories: 'Repositories', noRepositories: 'No repository is set up yet',
    noRepositoriesText: 'Open the configuration of this app and add a repository under “Repositories”: a name, the https address, your user name and an access token, and whether it is for the public or for private use. Any number of repositories from GitHub, GitLab, Gitea and others can be added.',
    legacyNotice: 'The repository of version 1 was moved into the list of repositories as “default”. It is marked as public because that is how it was exported before: secrets.yaml was always emptied. Change it to private in the configuration if the repository really is private.',
    audience_public: 'Public', audience_private: 'Private',
    audienceHintPublic: 'Meant for the public: private data is removed or censored.',
    audienceHintPrivate: 'Private use: secrets.yaml and other files are exported as they are.',
    branch: 'Branch', provider: 'Host', lastRun: 'Last run', never: 'Not run yet', address: 'Address',
    login: 'Login', hasLogin: 'access token set', noLogin: 'no login (only public repositories can be written)',
    disabled: 'switched off',
    previewBtn: 'Preview', exportBtn: 'Export now', exportAll: 'Export all', checkVisibility: 'Check visibility',
    checking: 'Checking…', running: 'Running…',
    vis_public: 'The repository is public: anyone can read it.',
    vis_private: 'The repository is not public.',
    vis_unknown: 'Whether the repository is public could not be found out ({0}).',
    vis_via_api: 'Answer of the {0} API', vis_via_anonymous: 'Anonymous access test',
    visibility: 'Visibility',
    heldTitle: 'This repository is public, but it is set to private use',
    heldText: 'Private use means secrets.yaml and other private files are exported as they are. Anyone on the internet could read them in this repository. Nothing has been pushed. You decide:',
    heldNoLogin: 'Make the repository private at your git host, or set it to “public” in the configuration so that private data is removed.',
    pushOnce: 'Push anyway, once', pushRemember: 'Push anyway and do not ask again', forget: 'Ask again from now on',
    acceptedNote: 'You accepted the public remote for this repository. Sensitive files go there as they are.',
    holdWarningInline: 'Held: the remote is public.',
    keepRunning: 'Keep the app running', keepRunningHint: 'Otherwise the app stops itself after {0} idle minutes.',
    stoppingIn: 'It stops in {0} min without activity.', stopNow: 'Stop the app now',
    r_pushed: 'Exported {0} changes and pushed them.', r_nothing: 'Nothing changed, nothing to commit.',
    r_preview: 'Preview: {0} new, {1} changed, {2} removed.',
    r_held_public_remote: 'Held: the repository is meant for private use but its remote is public. Nothing was pushed.',
    r_blocked_findings: 'Stopped: {0} private values were found and the checks are set to block.',
    r_no_url: 'No address is set for this repository.', r_disabled: 'Switched off.',
    r_no_sources: 'Nothing to export: no source folder is available.', r_error: 'Failed: {0}',
    status_ok: 'OK', status_held: 'Held', status_blocked: 'Stopped', status_error: 'Error', status_skipped: 'Skipped',

    previewIntro: 'A preview does everything an export does, except that it writes and pushes nothing: it shows which files are new, changed or removed in the repository. Unsaved changes from the Excludes tab are included, so you see their effect first.',
    previewFor: 'Repository', all: 'All repositories', run: 'Run preview', filter: 'Filter files…',
    added: 'new', modified: 'changed', removed: 'removed', unchanged: 'unchanged',
    showMore: 'Show more ({0} left)', nothingToShow: 'Nothing differs from the repository.',
    path: 'File', size: 'Size', censoredCount: '{0} censored',
    diffFor: 'Changes in {0}', diffBinary: 'Binary file, no text to compare.', loadingDiff: 'Loading…',
    secretsMasked: 'Values from secrets.yaml are shown as ••••.',
    skipped: 'Left out', tooLarge: '{0} files are larger than {1} MB and were left out.',
    blockedFiles: 'Not exported at all', findings: 'Censored in this repository',
    findingsNone: 'Nothing had to be censored.',
    cat_secrets: 'values from secrets.yaml', cat_keys: 'values of keys named like secrets', cat_urls: 'passwords in URLs',
    cat_mail: 'e-mail addresses', cat_ip: 'IP addresses', cat_mac: 'MAC addresses',
    w_secrets_unreadable: 'secrets.yaml is not valid YAML ({0}). Its values are still used as far as they can be read.',
    w_lovelace_unreadable: 'The dashboard file {0} could not be read.',
    w_supervisor_missing: 'The app options of your other apps are not exported: no connection to the Supervisor.',
    w_apps_unavailable: 'The app options could not be read: {0}',

    filesIntro: 'Everything that is in the folders this app can see, and what the exclude rules do to it. Greyed out entries are not exported. Changes you make here are drafts until you save them.',
    source: 'Folder', notAvailable: 'not available on this system', switchedOff: 'switched off in the export options',
    root: 'root', up: 'Up', summary: 'Summary of the top level', summaryBusy: 'Counting…',
    kept: 'Exported', left: 'Left out', files: 'files', empty: 'This folder is empty.', truncated: 'Only the first entries are shown.',
    excludeBtn: 'Exclude', keepBtn: 'Keep', included: 'exported', excluded: 'left out', tooLargeLabel: 'too large',
    why_mandatory: 'never exported (Home Assistant state)', why_custom: 'your pattern {0}', why_allow: 'only {0} is exported here',
    why_size: 'larger than the limit', why_separate: 'exported as its own folder', why_preset: 'preset “{0}” ({1})',
    searchHere: 'Filter this folder…', ruleAdded: 'Added the pattern {0} to the draft.',
    patternsApplyAll: 'A pattern with a leading slash is relative to the top of each folder.',

    excludesIntro: 'Presets cover what rarely belongs into a repository: databases, logs, caches, keys, large media. Switch them on or off, and add your own patterns below. Every change is shown in Files and Preview before you save it.',
    presets: 'Presets', onlyFor: 'only for: {0}', patterns: 'patterns', customTitle: 'Your own patterns',
    customHelp: 'One pattern per line, written like a .gitignore file: *.db for a name anywhere, deps/ for a folder, /tts/ for a folder at the top, custom_components/foo for a path, !keep.yaml to keep something back. The last matching pattern wins.',
    patternPlaceholder: 'for example *.bak or /www/community/', test: 'Test', add: 'Add', remove: 'Remove',
    noCustom: 'No patterns of your own.',
    testResult: '{0} files ({1}) would additionally be left out.', testNone: 'This pattern does not change anything.',
    testBack: '{0} files ({1}) would come back into the export.', testIncomplete: 'The folders are large; the count may be incomplete.',
    sizeLimit: 'Largest file to export', sizeLimitHint: 'Larger files are left out. In MB.',
    exportTitle: 'What is exported', ex_lovelace: 'Dashboards (Lovelace)', ex_addons: 'Options of the other apps',
    ex_addon_configs: 'App configuration folders', ex_esphome: 'ESPHome', ex_node_red: 'Node-RED flows',
    ex_local_apps: 'Local apps (the folder with your own apps)',
    mounts: 'Folders found', mountMissing: 'not mounted',

    checksIntro: 'The checks protect repositories that are set to public. Their files are censored before anything is written: values from secrets.yaml, IP and MAC addresses, secret-like keys, passwords in URLs and e-mail addresses.',
    checkEnabled: 'Checks', checkSecrets: 'Look for secrets', checkIps: 'Look for IP and MAC addresses',
    onFinding: 'When something is found', onFinding_censor: 'censor it and export', onFinding_block: 'stop the export',
    allowed: 'Allowed values', allowedHint: 'Texts that are never censored, for example a public address that is on purpose in your configuration.',
    extraSecrets: 'Extra secret values', extraSecretsHint: 'Values that are not in secrets.yaml but must never appear in a public repository.',
    noneYet: 'None yet.', addValue: 'Add a value',

    unsaved: 'Unsaved changes', saveBtn: 'Save to the app configuration', discard: 'Discard', saving: 'Saving…',
    saved: 'Saved. The next export uses these settings.', saveFailed: 'Saving failed: {0}',
    unsavedHint: 'The tabs show these changes already; nothing is stored until you save.',
    logIntro: 'The most recent lines of the app log.', refresh: 'Refresh',
    failed: 'This did not work: {0}',
    helpAllTitle: 'Writing patterns',
    stopped: 'The app is stopping. Start it again from Home Assistant when you need it.',
    loadingState: 'Loading…',
  },
  de: {
    tab_overview: 'Übersicht', tab_preview: 'Vorschau', tab_files: 'Dateien', tab_excludes: 'Ausschlüsse', tab_checks: 'Prüfungen',
    tab_log: 'Protokoll',
    release: 'Vorabversion {0}', busy: 'Läuft: {0}',
    repositories: 'Repositories', noRepositories: 'Noch kein Repository eingerichtet',
    noRepositoriesText: 'Öffne die Konfiguration dieser App und füge unter „Repositories“ eines hinzu: einen Namen, die https-Adresse, deinen Benutzernamen und ein Zugriffstoken, und ob es öffentlich oder privat genutzt wird. Beliebig viele Repositories von GitHub, GitLab, Gitea und anderen sind möglich.',
    legacyNotice: 'Das Repository aus Version 1 wurde als „default“ in die Liste der Repositories übernommen. Es ist als öffentlich markiert, weil es bisher so exportiert wurde: die secrets.yaml wurde immer geleert. Stelle es in der Konfiguration auf privat, wenn das Repository wirklich privat ist.',
    audience_public: 'Öffentlich', audience_private: 'Privat',
    audienceHintPublic: 'Für die Öffentlichkeit: private Daten werden entfernt oder zensiert.',
    audienceHintPrivate: 'Privat genutzt: secrets.yaml und andere Dateien werden unverändert exportiert.',
    branch: 'Branch', provider: 'Anbieter', lastRun: 'Letzter Lauf', never: 'Noch nicht gelaufen', address: 'Adresse',
    login: 'Zugang', hasLogin: 'Zugriffstoken gesetzt', noLogin: 'kein Zugang (nur öffentliche Repositories lassen sich beschreiben)',
    disabled: 'ausgeschaltet',
    previewBtn: 'Vorschau', exportBtn: 'Jetzt exportieren', exportAll: 'Alle exportieren', checkVisibility: 'Sichtbarkeit prüfen',
    checking: 'Prüfe…', running: 'Läuft…',
    vis_public: 'Das Repository ist öffentlich: jeder kann es lesen.',
    vis_private: 'Das Repository ist nicht öffentlich.',
    vis_unknown: 'Ob das Repository öffentlich ist, ließ sich nicht feststellen ({0}).',
    vis_via_api: 'Antwort der {0}-API', vis_via_anonymous: 'Test mit anonymem Zugriff',
    visibility: 'Sichtbarkeit',
    heldTitle: 'Dieses Repository ist öffentlich, aber für privaten Gebrauch eingestellt',
    heldText: 'Privater Gebrauch heißt: secrets.yaml und andere private Dateien werden unverändert exportiert. Jeder im Internet könnte sie in diesem Repository lesen. Es wurde nichts hochgeladen. Du entscheidest:',
    heldNoLogin: 'Stelle das Repository bei deinem Git-Anbieter auf privat, oder setze es in der Konfiguration auf „öffentlich“, damit private Daten entfernt werden.',
    pushOnce: 'Trotzdem hochladen, einmalig', pushRemember: 'Trotzdem hochladen und nicht mehr fragen', forget: 'Ab jetzt wieder nachfragen',
    acceptedNote: 'Du hast das öffentliche Repository dafür akzeptiert. Sensible Dateien landen dort unverändert.',
    holdWarningInline: 'Angehalten: das Repository ist öffentlich.',
    keepRunning: 'App weiterlaufen lassen', keepRunningHint: 'Sonst beendet sich die App nach {0} Minuten ohne Nutzung.',
    stoppingIn: 'Sie beendet sich in {0} Min ohne Aktivität.', stopNow: 'App jetzt beenden',
    r_pushed: '{0} Änderungen exportiert und hochgeladen.', r_nothing: 'Nichts geändert, nichts zu committen.',
    r_preview: 'Vorschau: {0} neu, {1} geändert, {2} entfernt.',
    r_held_public_remote: 'Angehalten: das Repository ist für privaten Gebrauch eingestellt, sein Ziel ist aber öffentlich. Nichts wurde hochgeladen.',
    r_blocked_findings: 'Gestoppt: {0} private Werte gefunden, die Prüfungen sind auf Stoppen eingestellt.',
    r_no_url: 'Für dieses Repository ist keine Adresse eingetragen.', r_disabled: 'Ausgeschaltet.',
    r_no_sources: 'Nichts zu exportieren: kein Quellordner verfügbar.', r_error: 'Fehlgeschlagen: {0}',
    status_ok: 'OK', status_held: 'Angehalten', status_blocked: 'Gestoppt', status_error: 'Fehler', status_skipped: 'Übersprungen',

    previewIntro: 'Eine Vorschau macht alles wie ein Export, schreibt und lädt aber nichts hoch: sie zeigt, welche Dateien im Repository neu, geändert oder entfernt würden. Ungespeicherte Änderungen aus dem Reiter Ausschlüsse sind enthalten, du siehst ihre Wirkung also vorher.',
    previewFor: 'Repository', all: 'Alle Repositories', run: 'Vorschau starten', filter: 'Dateien filtern…',
    added: 'neu', modified: 'geändert', removed: 'entfernt', unchanged: 'unverändert',
    showMore: 'Mehr anzeigen (noch {0})', nothingToShow: 'Nichts weicht vom Repository ab.',
    path: 'Datei', size: 'Größe', censoredCount: '{0} zensiert',
    diffFor: 'Änderungen in {0}', diffBinary: 'Binärdatei, kein Text zum Vergleichen.', loadingDiff: 'Lade…',
    secretsMasked: 'Werte aus der secrets.yaml werden als •••• angezeigt.',
    skipped: 'Ausgelassen', tooLarge: '{0} Dateien sind größer als {1} MB und wurden ausgelassen.',
    blockedFiles: 'Gar nicht exportiert', findings: 'In diesem Repository zensiert',
    findingsNone: 'Es musste nichts zensiert werden.',
    cat_secrets: 'Werte aus der secrets.yaml', cat_keys: 'Werte von Schlüsseln, die wie Geheimnisse heißen', cat_urls: 'Passwörter in URLs',
    cat_mail: 'E-Mail-Adressen', cat_ip: 'IP-Adressen', cat_mac: 'MAC-Adressen',
    w_secrets_unreadable: 'Die secrets.yaml ist kein gültiges YAML ({0}). Ihre Werte werden trotzdem verwendet, soweit lesbar.',
    w_lovelace_unreadable: 'Die Dashboard-Datei {0} ließ sich nicht lesen.',
    w_supervisor_missing: 'Die Optionen deiner anderen Apps werden nicht exportiert: keine Verbindung zum Supervisor.',
    w_apps_unavailable: 'Die App-Optionen ließen sich nicht lesen: {0}',

    filesIntro: 'Alles, was in den Ordnern liegt, die diese App sieht, und was die Ausschlussregeln damit machen. Ausgegraute Einträge werden nicht exportiert. Änderungen hier sind Entwürfe, bis du sie speicherst.',
    source: 'Ordner', notAvailable: 'auf diesem System nicht vorhanden', switchedOff: 'in den Export-Optionen ausgeschaltet',
    root: 'Wurzel', up: 'Hoch', summary: 'Übersicht der obersten Ebene', summaryBusy: 'Zähle…',
    kept: 'Exportiert', left: 'Ausgelassen', files: 'Dateien', empty: 'Dieser Ordner ist leer.', truncated: 'Es werden nur die ersten Einträge angezeigt.',
    excludeBtn: 'Ausschließen', keepBtn: 'Behalten', included: 'exportiert', excluded: 'ausgelassen', tooLargeLabel: 'zu groß',
    why_mandatory: 'wird nie exportiert (Zustand von Home Assistant)', why_custom: 'dein Muster {0}', why_allow: 'hier wird nur {0} exportiert',
    why_size: 'größer als das Limit', why_separate: 'wird als eigener Ordner exportiert', why_preset: 'Vorgabe „{0}“ ({1})',
    searchHere: 'Diesen Ordner filtern…', ruleAdded: 'Das Muster {0} wurde dem Entwurf hinzugefügt.',
    patternsApplyAll: 'Ein Muster mit Schrägstrich am Anfang gilt ab dem obersten Punkt jedes Ordners.',

    excludesIntro: 'Die Vorgaben decken ab, was selten in ein Repository gehört: Datenbanken, Protokolle, Caches, Schlüssel, große Medien. Schalte sie ein oder aus und ergänze unten eigene Muster. Jede Änderung siehst du in Dateien und Vorschau, bevor du speicherst.',
    presets: 'Vorgaben', onlyFor: 'nur für: {0}', patterns: 'Muster', customTitle: 'Deine eigenen Muster',
    customHelp: 'Ein Muster pro Zeile, geschrieben wie in einer .gitignore-Datei: *.db für einen Namen überall, deps/ für einen Ordner, /tts/ für einen Ordner ganz oben, custom_components/foo für einen Pfad, !behalten.yaml, um etwas zurückzuhalten. Das letzte passende Muster gewinnt.',
    patternPlaceholder: 'zum Beispiel *.bak oder /www/community/', test: 'Testen', add: 'Hinzufügen', remove: 'Entfernen',
    noCustom: 'Keine eigenen Muster.',
    testResult: '{0} Dateien ({1}) würden zusätzlich ausgelassen.', testNone: 'Dieses Muster ändert nichts.',
    testBack: '{0} Dateien ({1}) kämen wieder in den Export.', testIncomplete: 'Die Ordner sind groß; die Zahl kann unvollständig sein.',
    sizeLimit: 'Größte Datei beim Export', sizeLimitHint: 'Größere Dateien werden ausgelassen. In MB.',
    exportTitle: 'Was exportiert wird', ex_lovelace: 'Dashboards (Lovelace)', ex_addons: 'Optionen der anderen Apps',
    ex_addon_configs: 'Konfigurationsordner der Apps', ex_esphome: 'ESPHome', ex_node_red: 'Node-RED-Flows',
    ex_local_apps: 'Lokale Apps (der Ordner mit deinen eigenen Apps)',
    mounts: 'Gefundene Ordner', mountMissing: 'nicht eingebunden',

    checksIntro: 'Die Prüfungen schützen Repositories, die auf öffentlich stehen. Ihre Dateien werden zensiert, bevor etwas geschrieben wird: Werte aus der secrets.yaml, IP- und MAC-Adressen, Schlüssel mit Geheimnis-Namen, Passwörter in URLs und E-Mail-Adressen.',
    checkEnabled: 'Prüfungen', checkSecrets: 'Nach Geheimnissen suchen', checkIps: 'Nach IP- und MAC-Adressen suchen',
    onFinding: 'Wenn etwas gefunden wird', onFinding_censor: 'zensieren und exportieren', onFinding_block: 'den Export stoppen',
    allowed: 'Erlaubte Werte', allowedHint: 'Texte, die nie zensiert werden, zum Beispiel eine öffentliche Adresse, die absichtlich in deiner Konfiguration steht.',
    extraSecrets: 'Zusätzliche geheime Werte', extraSecretsHint: 'Werte, die nicht in der secrets.yaml stehen, aber nie in einem öffentlichen Repository auftauchen dürfen.',
    noneYet: 'Noch keine.', addValue: 'Wert hinzufügen',

    unsaved: 'Ungespeicherte Änderungen', saveBtn: 'In der App-Konfiguration speichern', discard: 'Verwerfen', saving: 'Speichere…',
    saved: 'Gespeichert. Der nächste Export verwendet diese Einstellungen.', saveFailed: 'Speichern fehlgeschlagen: {0}',
    unsavedHint: 'Die Reiter zeigen diese Änderungen schon; gespeichert wird erst mit dem Speichern.',
    logIntro: 'Die letzten Zeilen des App-Protokolls.', refresh: 'Aktualisieren',
    failed: 'Das hat nicht geklappt: {0}',
    helpAllTitle: 'Muster schreiben',
    stopped: 'Die App wird beendet. Starte sie bei Bedarf wieder in Home Assistant.',
    loadingState: 'Lade…',
  },
};

const lang = ((navigator.languages && navigator.languages[0]) || navigator.language || 'en').toLowerCase().startsWith('de') ? 'de' : 'en';
const t = (key, ...args) => {
  let text = (TEXT[lang] && TEXT[lang][key]) ?? TEXT.en[key] ?? key;
  args.forEach((value, index) => { text = text.split(`{${index}}`).join(value); });
  return text;
};

// ---- helpers ---------------------------------------------------------------------------------
function el(tag, props, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props || {})) {
    if (value === undefined || value === null || value === false) continue;
    if (key === 'class') node.className = value;
    else if (key === 'text') node.textContent = value;
    else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
    else if (value === true) node.setAttribute(key, '');
    else node.setAttribute(key, value);
  }
  const add = (child) => {
    if (Array.isArray(child)) child.forEach(add);
    else if (child !== null && child !== undefined && child !== false) node.append(child);
  };
  children.forEach(add);
  return node;
}

const ROOT = location.pathname.endsWith('/') ? location.pathname : `${location.pathname}/`;
async function api(path, body) {
  const response = await fetch(ROOT + path.replace(/^\//, ''), body === undefined ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || data.error || `HTTP ${response.status}`);
  return data;
}

const bytes = (n) => {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(n < 10240 ? 1 : 0)} KB`;
  if (n < 1024 ** 3) return `${(n / 1024 / 1024).toFixed(n < 10485760 ? 1 : 0)} MB`;
  return `${(n / 1024 ** 3).toFixed(1)} GB`;
};

const copy = (value) => JSON.parse(JSON.stringify(value));

// ---- state -----------------------------------------------------------------------------------
const S = {
  state: null, tab: 'overview', draft: null, baseline: '', saving: '', notice: '',
  visibility: {}, jobs: {}, preview: { repository: '', job: null, view: null, filter: '', status: '', shown: 300, diff: null },
  files: { source: 'config', path: '', filter: '', data: null, summary: null, busy: false },
  test: { pattern: '', result: null, error: '' }, log: [],
  timer: null,
};

const draftFrom = (state) => ({
  exclude: copy(state.exclude), presets: Object.fromEntries(state.presets.map((p) => [p.id, p.enabled])),
  export: copy(state.export), limits: copy(state.limits), allowed_secrets: copy(state.allowed_secrets),
  secrets: copy(state.secrets), check: copy(state.check),
});
const isDirty = () => !!S.draft && JSON.stringify(S.draft) !== S.baseline;

async function loadState(resetDraft = true) {
  S.state = await api('api/state');
  if (resetDraft || !S.draft) {
    S.draft = draftFrom(S.state);
    S.baseline = JSON.stringify(S.draft);
  }
  render();
}

// ---- messages --------------------------------------------------------------------------------
function resultText(result) {
  const args = result.args || {};
  switch (result.code) {
    case 'pushed': return t('r_pushed', args.changes);
    case 'nothing': return t('r_nothing');
    case 'preview': return t('r_preview', args.added, args.modified, args.removed);
    case 'held_public_remote': return t('r_held_public_remote');
    case 'blocked_findings': return t('r_blocked_findings', args.count);
    case 'no_url': return t('r_no_url');
    case 'disabled': return t('r_disabled');
    case 'no_sources': return t('r_no_sources');
    default: return t('r_error', args.message || result.code);
  }
}
const statusPill = (status) => el('span', { class: `pill ${status === 'ok' ? 'ok' : status === 'skipped' ? 'off' : status === 'held' ? 'warn' : 'bad'}`, text: t(`status_${status}`) });

const CATEGORY = { 'secret values': 'cat_secrets', 'values of secret-like keys': 'cat_keys', 'passwords in URLs': 'cat_urls', 'e-mail addresses': 'cat_mail', 'IP addresses': 'cat_ip', 'MAC addresses': 'cat_mac' };
const category = (name) => (CATEGORY[name] ? t(CATEGORY[name]) : name);

function warningText(code, args) {
  const keys = { secrets_unreadable: 'w_secrets_unreadable', lovelace_unreadable: 'w_lovelace_unreadable', supervisor_missing: 'w_supervisor_missing', apps_unavailable: 'w_apps_unavailable' };
  return keys[code] ? t(keys[code], args.error ?? args.name ?? '') : code;
}

function whyText(entry) {
  const origin = entry.origin || '';
  if (origin === 'mandatory') return t('why_mandatory');
  if (origin.startsWith('separate')) return t('why_separate');
  if (origin === 'custom') return t('why_custom', entry.rule);
  if (origin === 'allow') return t('why_allow', entry.rule);
  if (origin === 'size') return `${t('why_size')} (${entry.rule})`;
  if (origin.startsWith('preset:')) {
    const preset = S.state.presets.find((p) => p.id === origin.slice(7));
    return t('why_preset', preset ? preset.title[lang] : origin.slice(7), entry.rule);
  }
  return '';
}

// ---- jobs ------------------------------------------------------------------------------------
async function runJob(path, body, onProgress) {
  const { job } = await api(path, body);
  for (;;) {
    const view = await api(`api/job?id=${job}`);
    onProgress(view);
    if (view.done) return { job, view };
    await new Promise((resolve) => setTimeout(resolve, 700));
  }
}

// ---- tabs ------------------------------------------------------------------------------------
const TABS = ['overview', 'preview', 'files', 'excludes', 'checks', 'log'];

function renderTabs() {
  const nav = document.getElementById('tabs');
  nav.replaceChildren(...TABS.map((id) => el('button', {
    role: 'tab', 'aria-selected': String(S.tab === id), onclick: () => { S.tab = id; location.hash = id; render(); if (id === 'log') loadLog(); },
  }, t(`tab_${id}`), id === 'excludes' && isDirty() ? el('span', { class: 'count', text: '•' }) : null)));
}

function renderHeader() {
  const release = document.getElementById('release');
  const version = S.state.version;
  release.hidden = !/-/.test(version);
  release.textContent = release.hidden ? '' : t('release', version.replace(/^.*-(\w+)\.(\d+)$/, (m, name, n) => `${name[0].toUpperCase()}${name.slice(1)} ${n}`));
  const busy = document.getElementById('busy');
  const working = Object.values(S.jobs).find((job) => !job.done);
  busy.hidden = !working;
  busy.textContent = working ? t('busy', working.stage || '…') : '';
}

function renderSavebar() {
  const bar = document.getElementById('savebar');
  bar.hidden = !isDirty() && !S.notice;
  if (bar.hidden) return;
  const children = [];
  if (isDirty()) {
    children.push(el('strong', { text: t('unsaved') }), el('span', { class: 'muted grow', text: t('unsavedHint') }),
      el('button', { onclick: () => { S.draft = JSON.parse(S.baseline); S.test.result = null; S.files.data = null; render(); } }, t('discard')),
      el('button', { class: 'primary', disabled: !!S.saving, onclick: save }, S.saving || t('saveBtn')));
  } else {
    children.push(el('span', { class: 'grow', text: S.notice }), el('button', { onclick: () => { S.notice = ''; renderSavebar(); } }, '×'));
  }
  bar.replaceChildren(...children);
}

async function save() {
  S.saving = t('saving');
  renderSavebar();
  try {
    await api('api/save', { draft: S.draft });
    S.notice = t('saved');
    S.saving = '';
    await loadState(true);
  } catch (error) {
    S.saving = '';
    S.notice = t('saveFailed', error.message);
    render();
  }
}

function render() {
  if (!S.state) return;
  renderHeader();
  renderTabs();
  renderBanners();
  const panel = document.getElementById('panels');
  const views = { overview: viewOverview, preview: viewPreview, files: viewFiles, excludes: viewExcludes, checks: viewChecks, log: viewLog };
  panel.replaceChildren(views[S.tab]());
  renderSavebar();
}

function renderBanners() {
  const banners = document.getElementById('banners');
  const items = [];
  if (S.state.legacy_repository) items.push(el('div', { class: 'callout warn' }, el('p', { text: t('legacyNotice') })));
  banners.replaceChildren(...items);
}

// ---- overview --------------------------------------------------------------------------------
function visibilityBlock(repository) {
  const found = S.visibility[repository.slug];
  if (!found) return null;
  if (found === 'busy') return el('p', { class: 'muted' }, el('span', { class: 'spinner' }), t('checking'));
  const via = found.via === 'api' ? t('vis_via_api', found.provider) : found.via === 'anonymous' ? t('vis_via_anonymous') : '';
  const text = found.state === 'public' ? t('vis_public') : found.state === 'private' ? t('vis_private') : t('vis_unknown', found.detail || '');
  return el('p', { class: 'muted' }, el('strong', { text: `${t('visibility')}: ` }), text, via ? ` (${via})` : '');
}

function heldBlock(repository, lastResult) {
  const found = S.visibility[repository.slug];
  const publicRemote = found && found !== 'busy' && found.state === 'public';
  const heldNow = lastResult && lastResult.status === 'held';
  if (repository.audience !== 'private' || !(publicRemote || heldNow) || repository.allow_public_remote) return null;
  if (repository.accepted_public_remote) {
    return el('div', { class: 'callout warn' }, el('p', { text: t('acceptedNote') }),
      el('button', { class: 'small', onclick: async () => { await api('api/forget-public', { repository: repository.slug }); loadState(false); } }, t('forget')));
  }
  return el('div', { class: 'callout bad' },
    el('p', null, el('strong', { class: 'big', text: t('heldTitle') })),
    el('p', { text: t('heldText') }),
    el('p', { class: 'muted', text: t('heldNoLogin') }),
    el('div', { class: 'toolbar' },
      el('button', { class: 'danger', onclick: () => startExport(repository, true, false) }, t('pushOnce')),
      el('button', { class: 'danger', onclick: () => startExport(repository, true, true) }, t('pushRemember'))));
}

async function checkVisibility(repository) {
  S.visibility[repository.slug] = 'busy';
  render();
  try {
    S.visibility[repository.slug] = await api('api/visibility', { repository: repository.slug });
  } catch (error) {
    S.visibility[repository.slug] = { state: 'unknown', detail: error.message };
  }
  render();
}

async function startExport(repository, accept, remember) {
  const key = repository ? repository.slug : '*';
  S.jobs[key] = { done: false, stage: '' };
  render();
  try {
    const body = repository ? { repository: repository.slug, accept_public_remote: accept, remember } : {};
    const { view } = await runJob('api/export', body, (v) => { S.jobs[key] = v; renderHeader(); });
    S.jobs[key] = view;
  } catch (error) {
    S.jobs[key] = { done: true, results: [{ status: 'error', code: 'error', args: { message: error.message } }] };
  }
  await loadState(false);
}

function viewOverview() {
  const state = S.state;
  const nodes = [];
  if (!state.repositories.length) {
    nodes.push(el('div', { class: 'card' }, el('h2', { text: t('noRepositories') }), el('p', { text: t('noRepositoriesText') })));
  }
  if (state.repositories.length > 1) {
    nodes.push(el('div', { class: 'toolbar' }, el('button', { class: 'primary', disabled: state.busy, onclick: () => startExport(null) }, t('exportAll'))));
  }
  for (const repository of state.repositories) {
    const last = repository.last_run;
    const running = S.jobs[repository.slug] && !S.jobs[repository.slug].done;
    nodes.push(el('div', { class: 'card repo' },
      el('div', { class: 'head' },
        el('h2', { text: repository.name }),
        el('span', { class: `pill ${repository.audience}`, text: t(`audience_${repository.audience}`) }),
        !repository.enabled ? el('span', { class: 'pill off', text: t('disabled') }) : null,
        last ? statusPill(last.status) : null),
      el('p', { class: 'muted', text: repository.audience === 'public' ? t('audienceHintPublic') : t('audienceHintPrivate') }),
      el('dl', { class: 'facts' },
        el('dt', { text: t('address') }), el('dd', { class: 'mono', text: repository.url }),
        el('dt', { text: t('branch') }), el('dd', { text: repository.branch }),
        el('dt', { text: t('provider') }), el('dd', { text: repository.provider }),
        el('dt', { text: t('login') }), el('dd', { text: repository.has_login ? t('hasLogin') : t('noLogin') }),
        el('dt', { text: t('lastRun') }),
        el('dd', { text: last ? `${last.finished} · ${resultText(last)}` : t('never') })),
      visibilityBlock(repository),
      heldBlock(repository, last),
      el('div', { class: 'toolbar' },
        el('button', { disabled: state.busy, onclick: () => { S.tab = 'preview'; S.preview.repository = repository.slug; render(); runPreview(); } }, t('previewBtn')),
        el('button', { class: 'primary', disabled: state.busy || !repository.enabled, onclick: () => startExport(repository, false, false) },
          running ? [el('span', { class: 'spinner' }), t('running')] : t('exportBtn')),
        el('button', { onclick: () => checkVisibility(repository) }, t('checkVisibility')))));
  }
  const idleMinutes = state.behavior.stop_after_minutes;
  nodes.push(el('div', { class: 'card' },
    el('div', { class: 'toolbar' },
      el('label', { class: 'switch' }, el('input', { type: 'checkbox', checked: state.keep_running, onchange: async (event) => { await api('api/keep-running', { value: event.target.checked }); loadState(false); } }), el('span')),
      el('div', { class: 'grow' }, el('strong', { text: t('keepRunning') }),
        el('div', { class: 'muted', text: state.keep_running ? '' : `${t('keepRunningHint', idleMinutes)} ${t('stoppingIn', Math.max(0, idleMinutes - Math.floor(state.idle_seconds / 60)))}` })),
      el('button', { class: 'danger small', onclick: async () => { await api('api/stop', {}); document.getElementById('panels').replaceChildren(el('div', { class: 'callout' }, el('p', { text: t('stopped') }))); } }, t('stopNow')))));
  return el('section', { class: 'panel' }, nodes);
}

// ---- preview ---------------------------------------------------------------------------------
async function runPreview() {
  const preview = S.preview;
  preview.view = null;
  preview.diff = null;
  preview.job = null;
  S.jobs.preview = { done: false, stage: '' };
  render();
  try {
    const body = { draft: isDirty() ? S.draft : undefined };
    if (preview.repository) body.repository = preview.repository;
    const { job, view } = await runJob('api/preview', body, (v) => { S.jobs.preview = v; renderHeader(); });
    preview.job = job;
    preview.view = view;
    preview.shown = 300;
  } catch (error) {
    preview.view = { done: true, results: [{ status: 'error', code: 'error', args: { message: error.message }, repository: '' }] };
  }
  S.jobs.preview = { done: true };
  render();
}

async function showDiff(result, path) {
  S.preview.diff = { path, text: null, loading: true };
  render();
  try {
    const data = await api(`api/diff?job=${S.preview.job}&repository=${encodeURIComponent(result.slug)}&path=${encodeURIComponent(path)}`);
    S.preview.diff = { path, text: data.diff, binary: data.binary };
  } catch (error) {
    S.preview.diff = { path, text: error.message };
  }
  render();
}

function diffNode(diff) {
  if (diff.loading) return el('p', { class: 'muted' }, el('span', { class: 'spinner' }), t('loadingDiff'));
  if (diff.binary) return el('p', { class: 'muted', text: t('diffBinary') });
  const pre = el('pre', { class: 'diff' });
  for (const line of diff.text.split('\n')) {
    const header = line.startsWith('+++') || line.startsWith('---');
    const kind = header ? 'at' : line.startsWith('+') ? 'plus' : line.startsWith('-') ? 'minus' : line.startsWith('@@') ? 'at' : '';
    pre.append(el('span', { class: kind, text: `${line}\n` }));
  }
  return pre;
}

function resultPanel(result) {
  const preview = S.preview;
  const nodes = [];
  nodes.push(el('div', { class: 'toolbar' }, el('h2', { text: result.repository }), statusPill(result.status), el('span', { class: 'muted', text: resultText(result) })));
  if (result.status === 'error') return el('div', { class: 'card' }, nodes);
  const counts = result.counts || {};
  const filterStatus = preview.status;
  nodes.push(el('div', { class: 'chips' },
    ...['added', 'modified', 'removed'].map((status) => el('button', {
      class: `chip ${status}`, 'aria-pressed': String(filterStatus === status),
      onclick: () => { preview.status = filterStatus === status ? '' : status; preview.shown = 300; render(); },
    }, el('b', { text: String(counts[status] ?? 0) }), ` ${t(status)}`)),
    el('span', { class: 'chip', text: `${counts.unchanged ?? 0} ${t('unchanged')}` })));
  if (result.held) nodes.push(el('div', { class: 'callout bad' }, el('p', { text: t('r_held_public_remote') })));
  const warnings = (result.warnings || []).map(([code, args]) => el('li', { text: warningText(code, args) }));
  if (result.too_large) warnings.push(el('li', { text: t('tooLarge', result.too_large, S.state.limits.max_file_size_mb) }));
  const findings = Object.entries(result.findings || {});
  if (result.audience !== 'private' && findings.length) {
    nodes.push(el('p', null, el('strong', { text: `${t('findings')}: ` }), findings.map(([name, count]) => `${count} ${category(name)}`).join(', ')));
  }
  const blocked = Object.entries(result.blocked_files || {});
  if (blocked.length) warnings.push(el('li', { text: `${t('blockedFiles')}: ${blocked.map(([p, why]) => `${p} (${why})`).join(', ')}` }));
  if (warnings.length) nodes.push(el('ul', null, warnings));

  const needle = preview.filter.toLowerCase();
  const changes = (result.changes || []).filter((c) => (!filterStatus || c.status === filterStatus) && (!needle || c.path.toLowerCase().includes(needle)));
  if (!changes.length) {
    nodes.push(el('p', { class: 'muted', text: t('nothingToShow') }));
  } else {
    const rows = changes.slice(0, preview.shown).map((change) => el('tr', { class: 'click', onclick: () => showDiff(result, change.path) },
      el('td', null, el('span', { class: `status ${change.status}`, title: t(change.status), text: { added: '+', modified: '~', removed: '−' }[change.status] })),
      el('td', { class: 'mono', text: change.path }),
      el('td', null, change.censored ? el('span', { class: 'pill warn', text: t('censoredCount', change.censored) }) : null),
      el('td', { class: 'num', text: change.status === 'removed' ? bytes(change.old_size) : bytes(change.size) })));
    nodes.push(el('table', null, el('thead', null, el('tr', null, el('th'), el('th', { text: t('path') }), el('th'), el('th', { class: 'num', text: t('size') }))), el('tbody', null, rows)));
    if (changes.length > preview.shown) {
      nodes.push(el('button', { onclick: () => { preview.shown += 500; render(); } }, t('showMore', changes.length - preview.shown)));
    }
  }
  if (preview.diff) {
    nodes.push(el('h3', { text: t('diffFor', preview.diff.path) }), el('p', { class: 'muted', text: t('secretsMasked') }), diffNode(preview.diff));
  }
  return el('div', { class: 'card' }, nodes);
}

function viewPreview() {
  const preview = S.preview;
  const running = S.jobs.preview && !S.jobs.preview.done;
  const nodes = [
    el('p', { class: 'muted', text: t('previewIntro') }),
    el('div', { class: 'toolbar' },
      el('label', { text: `${t('previewFor')}: ` }),
      el('select', { onchange: (event) => { preview.repository = event.target.value; } },
        el('option', { value: '', text: t('all'), selected: !preview.repository }),
        ...S.state.repositories.map((r) => el('option', { value: r.slug, text: r.name, selected: preview.repository === r.slug }))),
      el('button', { class: 'primary', disabled: !!running || !S.state.repositories.length, onclick: runPreview },
        running ? [el('span', { class: 'spinner' }), t('running')] : t('run')),
      el('input', { type: 'text', placeholder: t('filter'), value: preview.filter, oninput: (event) => { preview.filter = event.target.value; preview.shown = 300; const start = event.target.selectionStart; render(); const box = document.querySelector('#panels input[type=text]'); if (box) { box.focus(); box.setSelectionRange(start, start); } } })),
  ];
  if (running && S.jobs.preview.stage) nodes.push(el('p', { class: 'muted', text: S.jobs.preview.stage }));
  if (preview.view) preview.view.results.forEach((result) => nodes.push(resultPanel(result)));
  return el('section', { class: 'panel' }, nodes);
}

// ---- files -----------------------------------------------------------------------------------
async function loadTree() {
  const files = S.files;
  files.busy = true;
  try {
    files.data = await api('api/tree', { source: files.source, path: files.path, draft: isDirty() ? S.draft : undefined });
  } catch (error) {
    files.data = { entries: [], error: error.message };
  }
  files.busy = false;
  render();
}

async function loadSummary() {
  S.files.summary = 'busy';
  render();
  try {
    S.files.summary = await api('api/summary', { source: S.files.source, draft: isDirty() ? S.draft : undefined });
  } catch (error) {
    S.files.summary = { entries: [], complete: true, error: error.message };
  }
  render();
}

const patternFor = (entry) => `/${entry.path}${entry.dir ? '/' : ''}`;
function addPattern(pattern) {
  if (!S.draft.exclude.includes(pattern)) S.draft.exclude.push(pattern);
  S.notice = '';
  S.files.data = null;
  S.files.summary = null;
  render();
}

function viewFiles() {
  const files = S.files;
  const sources = S.state.sources;
  const source = sources.find((s) => s.id === files.source) || sources[0];
  if (!files.data && !files.busy && source.available) loadTree();
  const nodes = [
    el('p', { class: 'muted', text: `${t('filesIntro')} ${t('patternsApplyAll')}` }),
    el('div', { class: 'toolbar' },
      ...sources.map((s) => el('button', {
        class: `chip`, 'aria-pressed': String(s.id === files.source), title: s.root || t('notAvailable'),
        onclick: () => { files.source = s.id; files.path = ''; files.data = null; files.summary = null; render(); },
      }, s.title[lang], !s.available ? ` (${t('notAvailable')})` : !s.enabled ? ` (${t('switchedOff')})` : ''))),
  ];
  if (!source.available) return el('section', { class: 'panel' }, nodes, el('div', { class: 'callout warn' }, el('p', { text: t('notAvailable') })));

  const crumbs = [el('button', { class: 'link', onclick: () => { files.path = ''; files.data = null; render(); } }, `${source.root}`)];
  let walked = '';
  for (const part of files.path.split('/').filter(Boolean)) {
    walked = walked ? `${walked}/${part}` : part;
    const target = walked;
    crumbs.push('/', el('button', { class: 'link', onclick: () => { files.path = target; files.data = null; render(); } }, part));
  }
  nodes.push(el('div', { class: 'crumbs mono' }, crumbs));
  nodes.push(el('div', { class: 'toolbar' },
    el('input', { type: 'text', placeholder: t('searchHere'), value: files.filter, oninput: (event) => { files.filter = event.target.value; const start = event.target.selectionStart; render(); const box = document.querySelector('#panels input[type=text]'); if (box) { box.focus(); box.setSelectionRange(start, start); } } }),
    el('button', { onclick: loadSummary, disabled: files.summary === 'busy' }, files.summary === 'busy' ? t('summaryBusy') : t('summary'))));

  if (files.summary && files.summary !== 'busy') {
    const rows = files.summary.entries.map((row) => el('tr', null,
      el('td', { class: 'mono', text: row.path + (row.dir ? '/' : '') }),
      el('td', { class: 'num', text: `${row.kept_files} ${t('files')} · ${bytes(row.kept_bytes)}` }),
      el('td', { class: 'num', text: `${row.left_files} ${t('files')} · ${bytes(row.left_bytes)}` })));
    nodes.push(el('table', null, el('thead', null, el('tr', null, el('th', { text: t('path') }), el('th', { class: 'num', text: t('kept') }), el('th', { class: 'num', text: t('left') }))), el('tbody', null, rows)));
  }

  const data = files.data;
  if (!data) {
    nodes.push(el('p', { class: 'muted' }, el('span', { class: 'spinner' }), t('loadingState')));
  } else if (data.error) {
    nodes.push(el('div', { class: 'callout bad' }, el('p', { text: data.error })));
  } else {
    const needle = files.filter.toLowerCase();
    const entries = data.entries.filter((e) => !needle || e.name.toLowerCase().includes(needle));
    const list = el('div', { class: 'tree' });
    if (files.path) {
      list.append(el('div', { class: 'entry' }, el('div', { class: 'name' }, el('button', { class: 'link', onclick: () => { files.path = files.path.split('/').slice(0, -1).join('/'); files.data = null; render(); } }, `↑ ${t('up')}`))));
    }
    for (const entry of entries) {
      const excluded = entry.status !== 'included';
      const canKeep = excluded && ['custom', 'preset'].includes((entry.origin || '').split(':')[0]);
      const canExclude = !excluded;
      list.append(el('div', { class: `entry ${excluded ? 'excluded' : ''}` },
        el('div', { class: 'name' },
          entry.dir ? el('button', { class: 'link', onclick: () => { files.path = entry.path; files.data = null; files.filter = ''; render(); } }, `📁 ${entry.name}`) : el('span', { class: 'label', text: `📄 ${entry.name}` })),
        el('div', { class: 'why', text: excluded ? (entry.status === 'too_large' ? `${t('tooLargeLabel')}: ${whyText(entry)}` : whyText(entry)) : '' }),
        el('div', { class: 'size', text: entry.dir ? '' : bytes(entry.size) }),
        el('div', null,
          canExclude ? el('button', { class: 'small', onclick: () => addPattern(patternFor(entry)) }, t('excludeBtn')) : null,
          canKeep ? el('button', { class: 'small', onclick: () => addPattern(`!${patternFor(entry)}`) }, t('keepBtn')) : null)));
    }
    if (!entries.length) list.append(el('p', { class: 'muted', text: t('empty') }));
    nodes.push(list);
    if (data.truncated) nodes.push(el('p', { class: 'muted', text: t('truncated') }));
  }
  return el('section', { class: 'panel' }, nodes);
}

// ---- excludes --------------------------------------------------------------------------------
function listEditor(values, onChange, { secret = false, empty = t('noneYet'), placeholder = '' } = {}) {
  const input = el('input', { type: secret ? 'password' : 'text', placeholder, autocomplete: 'off' });
  const add = () => { const value = input.value.trim(); if (value && !values.includes(value)) { onChange([...values, value]); } input.value = ''; };
  input.addEventListener('keydown', (event) => { if (event.key === 'Enter') { event.preventDefault(); add(); } });
  return el('div', null,
    el('div', { class: 'list' }, values.length ? values.map((value) => el('div', { class: 'item' },
      el('code', { text: secret ? '••••••••' : value }),
      el('button', { class: 'small', onclick: () => onChange(values.filter((v) => v !== value)) }, t('remove')))) : el('p', { class: 'muted', text: empty })),
    el('div', { class: 'add' }, input, el('button', { onclick: add }, t('addValue'))));
}

async function testPattern(pattern) {
  S.test.error = '';
  S.test.result = null;
  render();
  try {
    S.test.result = await api('api/pattern', { pattern, draft: S.draft });
  } catch (error) {
    S.test.error = error.message;
  }
  render();
}

function viewExcludes() {
  const draft = S.draft;
  const nodes = [el('p', { class: 'muted', text: t('excludesIntro') })];

  const presets = el('div', { class: 'card' }, el('h2', { text: t('presets') }),
    S.state.presets.map((preset) => el('div', { class: 'preset' },
      el('label', { class: 'switch' },
        el('input', { type: 'checkbox', checked: draft.presets[preset.id], onchange: (event) => { draft.presets[preset.id] = event.target.checked; S.files.data = null; S.files.summary = null; render(); } }), el('span')),
      el('div', { class: 'body' },
        el('div', { class: 'title', text: preset.title[lang] }),
        el('div', { class: 'muted', text: preset.description[lang] }),
        preset.sources ? el('div', { class: 'muted', text: t('onlyFor', preset.sources.map((id) => (S.state.sources.find((s) => s.id === id) || { title: { [lang]: id } }).title[lang]).join(', ')) }) : null,
        el('details', { class: 'patterns' }, el('summary', { text: `${preset.patterns.length} ${t('patterns')}` }), preset.patterns.map((p) => el('code', { text: p })))))));
  nodes.push(presets);

  const patternInput = el('input', { type: 'text', placeholder: t('patternPlaceholder'), value: S.test.pattern, autocomplete: 'off' });
  patternInput.addEventListener('input', () => { S.test.pattern = patternInput.value; });
  patternInput.addEventListener('keydown', (event) => { if (event.key === 'Enter') { event.preventDefault(); testPattern(patternInput.value.trim()); } });
  const result = S.test.result;
  const resultNode = S.test.error ? el('div', { class: 'callout bad' }, el('p', { text: S.test.error })) : result ? el('div', { class: 'callout' },
    el('p', { text: result.files === 0 ? t('testNone') : (result.examples[0] && !result.examples[0].now_excluded ? t('testBack', result.files, bytes(result.bytes)) : t('testResult', result.files, bytes(result.bytes))) }),
    result.complete ? null : el('p', { class: 'muted', text: t('testIncomplete') }),
    el('div', null, result.examples.map((e) => el('div', { class: 'mono muted', text: `${e.now_excluded ? '−' : '+'} ${e.path}` })))) : null;
  nodes.push(el('div', { class: 'card' }, el('h2', { text: t('customTitle') }), el('p', { class: 'muted', text: t('customHelp') }),
    el('div', { class: 'list' }, draft.exclude.length ? draft.exclude.map((pattern) => el('div', { class: 'item' }, el('code', { text: pattern }),
      el('button', { class: 'small', onclick: () => { draft.exclude = draft.exclude.filter((p) => p !== pattern); S.files.data = null; render(); } }, t('remove')))) : el('p', { class: 'muted', text: t('noCustom') })),
    el('div', { class: 'add' }, patternInput,
      el('button', { onclick: () => testPattern(patternInput.value.trim()) }, t('test')),
      el('button', { class: 'primary', onclick: () => { const value = patternInput.value.trim(); if (value) { S.test.pattern = ''; S.test.result = null; addPattern(value); } } }, t('add'))),
    resultNode));

  nodes.push(el('div', { class: 'card' }, el('h2', { text: t('sizeLimit') }), el('p', { class: 'muted', text: t('sizeLimitHint') }),
    el('input', { type: 'number', min: '1', value: String(draft.limits.max_file_size_mb), onchange: (event) => { draft.limits.max_file_size_mb = Math.max(1, parseInt(event.target.value, 10) || 1); S.files.data = null; render(); } })));

  nodes.push(el('div', { class: 'card' }, el('h2', { text: t('exportTitle') }),
    ['lovelace', 'addons', 'addon_configs', 'esphome', 'node_red', 'local_apps'].map((key) => el('div', { class: 'preset' },
      el('label', { class: 'switch' }, el('input', { type: 'checkbox', checked: draft.export[key], onchange: (event) => { draft.export[key] = event.target.checked; S.files.data = null; render(); } }), el('span')),
      el('div', { class: 'body' }, el('div', { class: 'title', text: t(`ex_${key}`) }))))));
  const mounts = Object.entries(S.state.mounts).map(([kind, found]) => `${kind}: ${found.length ? found.join(', ') : t('mountMissing')}`);
  nodes.push(el('p', { class: 'muted', text: `${t('mounts')}: ${mounts.join(' · ')}` }));
  return el('section', { class: 'panel' }, nodes);
}

// ---- checks ----------------------------------------------------------------------------------
function viewChecks() {
  const check = S.draft.check;
  const toggle = (key, label) => el('div', { class: 'preset' },
    el('label', { class: 'switch' }, el('input', { type: 'checkbox', checked: check[key], onchange: (event) => { check[key] = event.target.checked; render(); } }), el('span')),
    el('div', { class: 'body' }, el('div', { class: 'title', text: label })));
  return el('section', { class: 'panel' },
    el('p', { class: 'muted', text: t('checksIntro') }),
    el('div', { class: 'card' }, toggle('enabled', t('checkEnabled')), toggle('check_for_secrets', t('checkSecrets')), toggle('check_for_ips', t('checkIps')),
      el('div', { class: 'toolbar' }, el('label', { text: `${t('onFinding')}: ` }),
        el('select', { onchange: (event) => { check.on_finding = event.target.value; render(); } },
          ['censor', 'block'].map((value) => el('option', { value, text: t(`onFinding_${value}`), selected: check.on_finding === value }))))),
    el('div', { class: 'card' }, el('h2', { text: t('allowed') }), el('p', { class: 'muted', text: t('allowedHint') }),
      listEditor(S.draft.allowed_secrets, (values) => { S.draft.allowed_secrets = values; render(); })),
    el('div', { class: 'card' }, el('h2', { text: t('extraSecrets') }), el('p', { class: 'muted', text: t('extraSecretsHint') }),
      listEditor(S.draft.secrets, (values) => { S.draft.secrets = values; render(); }, { secret: true })));
}

// ---- log -------------------------------------------------------------------------------------
async function loadLog() {
  try {
    S.log = (await api('api/log')).lines;
  } catch (error) {
    S.log = [{ time: '', level: 'ERROR', message: error.message }];
  }
  if (S.tab === 'log') render();
}

function viewLog() {
  const box = el('pre', { class: 'logbox' }, S.log.map((line) => el('span', { class: line.level, text: `${line.time} ${line.level} ${line.message}\n` })));
  return el('section', { class: 'panel' }, el('div', { class: 'toolbar' }, el('span', { class: 'muted grow', text: t('logIntro') }), el('button', { onclick: loadLog }, t('refresh'))), box);
}

// ---- start -----------------------------------------------------------------------------------
document.title = 'Home Assistant Git Exporter';
const initial = location.hash.slice(1);
if (TABS.includes(initial)) S.tab = initial;
loadState().catch((error) => {
  document.getElementById('panels').replaceChildren(el('div', { class: 'callout bad' }, el('p', { text: t('failed', error.message) })));
});
