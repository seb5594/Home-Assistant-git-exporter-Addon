#!/usr/bin/env bashio
set -e

# Enable Jemalloc for better memory handling
export LD_PRELOAD="/usr/local/lib/libjemalloc.so.2"

local_repository='/data/repository'
pull_before_push="$(bashio::config 'repository.pull_before_push')"

# ----------------------------
# Git Setup
# ----------------------------
function setup_git {
    repository=$(bashio::config 'repository.url')
    username=$(bashio::config 'repository.username')
    password=$(bashio::config 'repository.password')
    commiter_mail=$(bashio::config 'repository.email')
    branch=$(bashio::config 'repository.branch_name')
    ssl_verify=$(bashio::config 'repository.ssl_verification')

    # URL encode password unless it's a GitHub token
    if [[ "$password" != ghp_* ]] && [[ "$password" != github_pat_* ]]; then
        password=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${password}'))")
    fi

    [ ! -d "$local_repository" ] && mkdir -p "$local_repository"

    if [ ! -d "$local_repository/.git" ]; then
        fullurl="https://${username}:${password}@${repository##*https://}"
        if [ "$pull_before_push" == 'true' ]; then
            bashio::log.info 'Cloning existing repository...'
            git clone "$fullurl" "$local_repository" || bashio::log.warning "Repository already exists, skipping clone."
        else
            bashio::log.info 'Initializing new repository...'
            git init "$local_repository"
            git remote add origin "$fullurl"
        fi
        cd "$local_repository"
        git checkout "$branch" 2>/dev/null || true
        git config user.name "$username"
        git config user.email "${commiter_mail:-git.exporter@home-assistant}"
    else
        cd "$local_repository"
        bashio::log.info 'Repository already exists, using existing folder.'
    fi

    # Reset git secrets
    git config --unset-all 'secrets.allowed' || true
    git config --unset-all 'secrets.patterns' || true
    git config --unset-all 'secrets.providers' || true

    if [ "$pull_before_push" == 'true' ]; then
        bashio::log.info 'Pulling latest changes...'
        git fetch || bashio::log.warning 'Git fetch failed, continuing...'
        git reset --hard "origin/$branch" || bashio::log.warning 'Git reset failed, continuing...'
    fi

    git clean -f -d
}

# ----------------------------
# Secrets Check
# ----------------------------
function check_secrets {
    bashio::log.info 'Adding secrets patterns...'

    git secrets --add -a '!secret'

    for pattern in \
        "password:\s?[\'\"]?\w+[\'\"]?\n?" \
        "token:\s?[\'\"]?\w+[\'\"]?\n?" \
        "client_id:\s?[\'\"]?\w+[\'\"]?\n?" \
        "api_key:\s?[\'\"]?\w+[\'\"]?\n?" \
        "chat_id:\s?[\'\"]?\w+[\'\"]?\n?" \
        "allowed_chat_ids:\s?[\'\"]?\w+[\'\"]?\n?" \
        "latitude:\s?[\'\"]?\w+[\'\"]?\n?" \
        "longitude:\s?[\'\"]?\w+[\'\"]?\n?" \
        "credential_secret:\s?[\'\"]?\w+[\'\"]?\n?"; do
        git secrets --add "$pattern"
    done

    [ "$(bashio::config 'check.check_for_secrets')" == 'true' ] && \
        git secrets --add-provider -- sed '/^$/d;/^#.*/d;/^&/d;s/^.*://g;s/\s//g' /config/secrets.yaml

    if [ "$(bashio::config 'check.check_for_ips')" == 'true' ]; then
        git secrets --add '([0-9]{1,3}\.){3}[0-9]{1,3}'
        git secrets --add '([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
        git secrets --add -a --literal 'AA:BB:CC:DD:EE:FF'
        git secrets --add -a --literal '123.456.789.123'
        git secrets --add -a --literal '0.0.0.0'
    fi

    bashio::log.info 'Adding custom secrets...'
    readarray -t <<<"$(bashio::config 'secrets' | grep -v '^$')"
    if [ -n "$MAPFILE" ] && [ ${#MAPFILE[@]} -gt 0 ]; then
        for secret in "${MAPFILE[@]}"; do
            git secrets --add "$secret"
        done
    fi

    readarray -t <<<"$(bashio::config 'allowed_secrets' | grep -v '^$')"
    if [ -n "$MAPFILE" ] && [ ${#MAPFILE[@]} -gt 0 ]; then
        for allowed_secret in "${MAPFILE[@]}"; do
            git secrets --add -a "$allowed_secret"
        done
    fi

    bashio::log.info 'Scanning repository for secrets...'
    git secrets --scan $(find "$local_repository" -name '*.yaml' -o -name '*.yml' -o -name '*.json' -o -name '*.disabled') \
        || (bashio::log.error 'Secrets found! Fix them before committing.' && exit 1)
}

# ----------------------------
# Export Functions
# ----------------------------
# (hier bleiben deine bisherigen export_* Funktionen unverändert)
# ----------------------------
# Cleanup & Permission Normalization
# ----------------------------
function cleanup_repo_files {
    bashio::log.info "Cleaning repository before commit..."

    # Remove excluded files
    excludes=($(bashio::config 'exclude'))
    excludes=("secrets.yaml" ".storage" ".cloud" "esphome/" ".uuid" "node-red/" "addons_config/" "${excludes[@]}")
    for pattern in "${excludes[@]}"; do
        find "$local_repository" -path "$local_repository/$pattern" 2>/dev/null | while read -r file; do
            [ -e "$file" ] && rm -rf "$file" || bashio::log.warning "Could not remove $file, skipping..."
        done
    done

    # Remove binary files except text/bash scripts
    find "$local_repository" -type f ! -name "*.sh" ! -name "*.yaml" ! -name "*.yml" ! -name "*.json" ! -name "*.js" -print0 2>/dev/null |
    while IFS= read -r -d '' file; do
        file_type=$(file "$file")
        if echo "$file_type" | grep -qE 'executable|binary|ELF|PE32'; then
            bashio::log.info "Removing binary file: $file"
            rm -f "$file" || bashio::log.warning "Could not remove $file, skipping..."
        fi
    done

    # Normalize permissions
    find "${local_repository}" -type d -exec chmod 755 {} \; 2>/dev/null
    find "${local_repository}" -type f -exec chmod 644 {} \; 2>/dev/null
    find "${local_repository}" -type f -name "*.sh" -exec chmod 755 {} \; 2>/dev/null
    chown -R root:root "$local_repository"

    bashio::log.info "✅ Cleanup complete."
}

# ----------------------------
# Main
# ----------------------------
bashio::log.info 'Starting git export...'

setup_git
export_ha_config
[ "$(bashio::config 'export.lovelace')" == 'true' ] && export_lovelace
[ "$(bashio::config 'export.esphome')" == 'true' ] && [ -d '/config/esphome' ] && export_esphome
[ "$(bashio::config 'export.addons')" == 'true' ] && export_addons
[ "$(bashio::config 'export.addon_configs')" == 'true' ] && export_addon_configs
[ "$(bashio::config 'export.node_red')" == 'true' ] && [ -d '/config/node-red' ] && export_node_red
[ "$(bashio::config 'check.enabled')" == 'true' ] && check_secrets

if [ "$(bashio::config 'dry_run')" == 'true' ]; then
    git status
else
    cleanup_repo_files
    bashio::log.info 'Committing changes and pushing to remote...'
    git add .
    commit_msg="$(bashio::config 'repository.commit_message')"
    commit_msg="${commit_msg//\{DATE\}/$(date +'%Y-%m-%d %H:%M:%S')}"
    git commit -m "$commit_msg"
    if [ "$pull_before_push" != 'true' ]; then
        git push --set-upstream origin "$branch" -f
    else
        git push origin
    fi
fi

bashio::log.info 'Exporter finished. Stopping add-on...'
[ -n "$(bashio::addon.slug)" ] && bashio::addon.stop || true
bashio::log.info '✅ Git Export complete.'
exit 0
