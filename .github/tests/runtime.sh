#!/usr/bin/env bash
set -Eeuo pipefail

# Exercise the real export functions; mock only Supervisor and the Git remote.
fixture=$(mktemp -d)
trap 'rm -rf -- "$fixture"' EXIT
bashio::log.info() { :; }
bashio::config() {
    case "$1" in
        repository.url) echo 'https://example.invalid/test.git' ;;
        repository.username) echo 'ci' ;;
        repository.password) echo "quote'and space" ;;
        repository.branch_name) echo 'main' ;;
        repository.email) echo 'ci@example.invalid' ;;
        *) echo 'false' ;;
    esac
}
# shellcheck source=git-exporter/root/run.sh
source "${RUN_SCRIPT:-/run.sh}"
local_repository="$fixture/repository"
git() {
    case "$1" in
        clone) mkdir -p "$3/.git" ;;
        fetch) test "$PWD" == "$local_repository" ;;
        rev-parse) return 1 ;;
    esac
}
setup_git
test "$PWD" == "$local_repository"
test "$password" == 'quote%27and%20space'
echo 'PASS: first clone enters repository and safely encodes credentials'

bashio::addons.installed() { echo 'test_app'; }
bashio::addon.options() { echo '{"sample":"retained"}'; }
bashio::api.supervisor() { echo '[{"name":"Test","source":"https://example.invalid/apps","slug":"test"}]'; }
export_addons
test -f "$local_repository/addons/test_app.yaml"
grep -q 'sample: retained' "$local_repository/addons/test_app.yaml"
test -f "$local_repository/addons/repositories.yaml"
echo 'PASS: app options survive rsync synchronization'
