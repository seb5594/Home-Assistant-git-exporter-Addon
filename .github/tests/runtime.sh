#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s inherit_errexit

# Runs inside the built image (release pipeline). The unit tests of the exporter run against the
# installed package, then the real service is started and asked for its state.
TESTS_DIR="${TESTS_DIR:-/tests}"
SERVICE="${SERVICE_DIR:-/etc/s6-overlay/s6-rc.d/git-exporter}"

pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

if ! { python3 --version && git --version && python3 -c 'import yaml'; } >/dev/null 2>&1; then
  fail 'python, git or PyYAML is missing'
fi
pass 'python, git and PyYAML are installed'

for script in "$SERVICE/run" "$SERVICE/finish"; do bash -n "$script"; done
pass 'the service scripts parse'

[[ -d "$TESTS_DIR" ]] || fail "the test folder $TESTS_DIR is not mounted"
export GIT_CONFIG_GLOBAL=/dev/null GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.org \
  GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.org
output="$(cd "$TESTS_DIR" && python3 -m unittest discover -s "$TESTS_DIR" -v 2>&1)" || {
  printf '%s\n' "$output" >&2
  fail 'the unit tests failed'
}
# One PASS line for every test that ran; the pipeline counts them.
grep -E ' \.\.\. ok$' <<<"$output" | sed -E 's/^([^ ]+) \(([^)]*)\).* \.\.\. ok$/PASS: \2/' || true

# The service itself, without a Supervisor.
work="$(mktemp -d)"
trap 'kill "${pid:-}" 2>/dev/null || true; rm -rf "$work"' EXIT
echo '{"repositories": [], "behavior": {"export_on_start": false, "keep_running": true}}' >"$work/options.json"
mkdir "$work/data"
OPTIONS_FILE="$work/options.json" DATA_DIR="$work/data" INGRESS_PORT=18099 VERSION_FILE="${VERSION_FILE:-/etc/git-exporter/version}" \
  python3 -m exporter >"$work/service.log" 2>&1 &
pid=$!
for _ in $(seq 1 50); do
  curl -fs -o /dev/null http://127.0.0.1:18099/api/state && break
  sleep 0.2
done
state="$(curl -fsS http://127.0.0.1:18099/api/state)" || { cat "$work/service.log" >&2; fail 'the service did not come up'; }
[[ "$(python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])' <<<"$state")" =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]] || fail 'the service reports no version'
curl -fs http://127.0.0.1:18099/ | grep -q '<html' || fail 'the web interface is not served'
pass 'the service starts and serves the web interface'
