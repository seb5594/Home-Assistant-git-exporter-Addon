#!/usr/bin/env bashio
set -e

# Enable Jemalloc for better memory handling
export LD_PRELOAD="/usr/local/lib/libjemalloc.so.2"

local_repository='/data/repository'
pull_before_push="$(bashio::config 'repository.pull_before_push')"

function setup_git {
    repository=$(bashio::config 'repository.url')
    username=$(bashio::config 'repository.username')
    password=$(bashio::config 'repository.password')
    commiter_mail=$(bashio::config 'repository.email')
    branch=$(bashio::config 'repository.branch_name')
    ssl_verify=$(bashio::config 'repository.ssl_verification')

    if [[ "$password" != "ghp_*" ]]  && [[ "$password" != "github_pat_*" ]]; then
        password=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${password}'))")
    fi

    if [ ! -d $local_repository ]; then
        bashio::log.info 'Create local repository'
        mkdir -p $local_repository
    fi
    cd $local_repository

    if [ "${ssl_verify:-true}" == 'false' ]; then
        bashio::log.info 'Disabling SSL verification for git repositories'
        git config --global http.sslVerify false
    fi

    if [ ! -d .git ]; then
        fullurl="https://${username}:${password}@${repository##*https://}"
        if [ "$pull_before_push" == 'true' ]; then
            bashio::log.info 'Clone existing repository'
            git clone "$fullurl" $local_repository
            git checkout "$branch"
        else
            bashio::log.info 'Initialize new repository'
            git init $local_repository
            git remote add origin "$fullurl"
        fi
        git config user.name "${username}"
        git config user.email "${commiter_mail:-git.exporter@home-assistant}"
    fi

    # Reset secrets if existing
    git config --unset-all 'secrets.allowed' || true
    git config --unset-all 'secrets.patterns' || true
    git config --unset-all 'secrets.providers' || true

    if [ "$pull_before_push" == 'true' ]; then
        bashio::log.info 'Pull latest'
        git fetch
        git reset --hard "origin/$branch"
    fi

    git clean -f -d
}

function check_secrets {
    bashio::log.info 'Add secrets pattern'

    # Allow !secret lines
    git secrets --add -a '!secret'

    # Set prohibited patterns
    git secrets --add "password:\s?[\'\"]?\w+[\'\"]?\n?"
    git secrets --add "token:\s?[\'\"]?\w+[\'\"]?\n?"
    git secrets --add "client_id:\s?[\'\"]?\w+[\'\"]?\n?"
    git secrets --add "api_key:\s?[\'\"]?\w+[\'\"]?\n?"
    git secrets --add "chat_id:\s?[\'\"]?\w+[\'\"]?\n?"
    git secrets --add "allowed_chat_ids:\s?[\'\"]?\w+[\'\"]?\n?"
    git secrets --add "latitude:\s?[\'\"]?\w+[\'\"]?\n?"
    git secrets --add "longitude:\s?[\'\"]?\w+[\'\"]?\n?"
    git secrets --add "credential_secret:\s?[\'\"]?\w+[\'\"]?\n?"

    if [ "$(bashio::config 'check.check_for_secrets')" == 'true' ]; then
        git secrets --add-provider -- sed '/^$/d;/^#.*/d;/^&/d;s/^.*://g;s/\s//g' /config/secrets.yaml
    fi

    if [ "$(bashio::config 'check.check_for_ips')" == 'true' ]; then
        git secrets --add '([0-9]{1,3}\.){3}[0-9]{1,3}'
        git secrets --add '([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'

        # Allow dummy / general ips and mac
        git secrets --add -a --literal 'AA:BB:CC:DD:EE:FF'
        git secrets --add -a --literal '123.456.789.123'
        git secrets --add -a --literal '0.0.0.0'
    fi

    bashio::log.info 'Add secrets from secrets.yaml'
    prohibited_patterns=$(git config --get-all secrets.patterns)
    bashio::log.info "Prohibited patterns:\n${prohibited_patterns//\\n/\\\\n}"

    readarray -t <<<"$(bashio::config 'secrets' | grep -v '^$')"
    if [ -n "$MAPFILE" ] && [ ${#MAPFILE[@]} -gt 0 ]; then
        bashio::log.info 'Add custom secrets'
        for secret in "${MAPFILE[@]}"; do
            git secrets --add "$secret"
        done
    fi

    readarray -t <<<"$(bashio::config 'allowed_secrets' | grep -v '^$')"
    if [ -n "$MAPFILE" ] && [ ${#MAPFILE[@]} -gt 0 ]; then
        bashio::log.info 'Add custom allowed secrets'
        for allowed_secret in "${MAPFILE[@]}"; do
            git secrets --add -a "$allowed_secret"
        done
    fi

    bashio::log.info 'Checking for secrets'
    git secrets --scan $(find $local_repository -name '*.yaml' -o -name '*.yml' -o -name '*.json' -o -name '*.disabled') \
    || (bashio::log.error 'Found secrets in files!!! Fix them to be able to commit! See https://www.home-assistant.io/docs/configuration/secrets/ for more information!' && exit 1)
}

function export_ha_config {
    bashio::log.info 'Export Home Assistant configuration'
    excludes=$(bashio::config 'exclude')
    excludes=("secrets.yaml" ".storage" ".cloud" "esphome/" ".uuid" "node-red/" "${excludes[@]}")
    [ -d "${local_repository}/config/esphome" ] && rm -r "${local_repository}/config/esphome"
    exclude_args=$(printf -- '--exclude=%s ' ${excludes[@]})
    rsync -av --compress --delete --checksum --prune-empty-dirs -q --include='.gitignore' $exclude_args /config/ "${local_repository}/config/"
    sed 's/:.*$/: ""/g' /config/secrets.yaml > "${local_repository}/config/secrets.yaml"
    chmod 644 -R "${local_repository}/config"
}

function export_lovelace {
    bashio::log.info 'Export Lovelace configuration'
    [ ! -d "${local_repository}/lovelace" ] && mkdir -p "${local_repository}/lovelace"
    mkdir -p '/tmp/lovelace'
    find /config/.storage -name "lovelace*" -printf '%f\n' | xargs -I % cp /config/.storage/% /tmp/lovelace/%.json
    /utils/jsonToYaml.py '/tmp/lovelace/' 'data'
    rsync -av --compress --delete --checksum --prune-empty-dirs -q --include='*.yaml' --exclude='*' /tmp/lovelace/ "${local_repository}/lovelace"
    chmod 644 -R "${local_repository}/lovelace"
}

function export_esphome {
    bashio::log.info 'Export ESPHome configuration'
    rsync -av --compress --delete --checksum --prune-empty-dirs -q \
         --exclude='.esphome*' --include='*/' --include='.gitignore' --include='*.yaml' --include='*.disabled' --exclude='secrets.yaml' --exclude='*' \
        /config/esphome/ "${local_repository}/esphome/"
    [ -f /config/esphome/secrets.yaml ] && sed 's/:.*$/: ""/g' /config/esphome/secrets.yaml > "${local_repository}/esphome/secrets.yaml"
    chmod 644 -R ${local_repository}/esphome
}

function export_addons {
    [ -d ${local_repository}/addons ] || mkdir -p ${local_repository}/addons
    installed_addons=$(bashio::addons.installed)
    mkdir -p '/tmp/addons/'
    for addon in $installed_addons; do
        if [ "$(bashio::addons.installed "${addon}")" == 'true' ]; then
            bashio::log.info "Get ${addon} configs"
            bashio::addon.options "$addon" > /tmp/tmp.json
            /utils/jsonToYaml.py /tmp/tmp.json
            mv /tmp/tmp.yaml "/tmp/addons/${addon}.yaml"
        fi
    done
    bashio::log.info "Get addon repositories"
    bashio::api.supervisor GET "/store/repositories" false \
      | jq '. | map(select(.source != null and .source != "core" and .source != "local")) | map({(.name): {source,maintainer,slug}}) | add' > /tmp/tmp.json
    /utils/jsonToYaml.py /tmp/tmp.json
    mv /tmp/tmp.yaml "/tmp/addons/repositories.yaml"
    rsync -av --compress --delete --checksum --prune-empty-dirs -q /tmp/addons/ ${local_repository}/addons
    chmod 644 -R ${local_repository}/addons
}

function export_addon_configs {
    if bashio::config.true 'export.addon_configs'; then
        bashio::log.info "Exporting /addon_configs directory..."
        mkdir -p "${local_repository}/addons_config"
        rsync -av --delete /addon_configs/ "${local_repository}/addons_config/" --exclude '.git'
        chmod 644 -R "${local_repository}/addons_config"
        bashio::log.info "Addon configs exported successfully"
    else
        bashio::log.info "Addon config export disabled"
    fi
}

function export_node-red {
    bashio::log.info 'Export Node-RED flows'
    rsync -av --compress --delete --checksum --prune-empty-dirs -q \
          --exclude='flows_cred.json' --exclude='*.backup' --include='flows.json' --include='settings.js' --exclude='*' \
        /config/node-red/ ${local_repository}/node-red
    chmod 644 -R ${local_repository}/node-red
}

function cleanup_repo_files {
    bashio::log.info "Cleaning up repository before commit..."

    # Remove excluded files
    excludes=$(bashio::config 'exclude')
    excludes=("secrets.yaml" ".storage" ".cloud" "esphome/" ".uuid" "node-red/" "addons_config/" "${excludes[@]}")
    for pattern in "${excludes[@]}"; do
        find "$local_repository" -path "$local_repository/$pattern" -exec rm -rf {} +
    done

    # Remove binary files except text/bash scripts
    find "$local_repository" -type f ! -name "*.sh" ! -name "*.yaml" ! -name "*.yml" ! -name "*.json" ! -name "*.js" -print0 |
    while IFS= read -r -d '' file; do
        file_type=$(file "$file")
        if echo "$file_type" | grep -qE 'executable|binary|ELF|PE32'; then
            bashio::log.info "Removing binary file from repo: $file"
            rm -f "$file"
        fi
    done

    # Normalize permissions
    find "${local_repository}" -type d -exec chmod 755 {} \;
    find "${local_repository}" -type f -exec chmod 644 {} \;
    find "${local_repository}" -type f -name "*.sh" -exec chmod 755 {} \;
    chown -R root:root "${local_repository}"

    bashio::log.info "✅ Cleanup complete."
}

bashio::log.info 'Start git export'

setup_git
export_ha_config
[ "$(bashio::config 'export.lovelace')" == 'true' ] && export_lovelace
[ "$(bashio::config 'export.esphome')" == 'true' ] && [ -d '/config/esphome' ] && export_esphome
[ "$(bashio::config 'export.addons')" == 'true' ] && export_addons
[ "$(bashio::config 'export.addon_configs')" == 'true' ] && export_addon_configs
[ "$(bashio::config 'export.node_red')" == 'true' ] && [ -d '/config/node-red' ] && export_node-red
[ "$(bashio::config 'check.enabled')" == 'true' ] && check_secrets

if [ "$(bashio::config 'dry_run')" == 'true' ]; then
    git status
else
    cleanup_repo_files

    bashio::log.info 'Commit changes and push to remote'
    git add .
    commit_msg="$(bashio::config 'repository.commit_message')"
    commit_msg="${commit_msg//\{DATE\}/$(date +'%Y-%m-%d %H:%M:%S')}"
    git commit -m "$commit_msg"
    if [ ! "$pull_before_push" == 'true' ]; then
        git push --set-upstream origin "$branch" -f
    else
        git push origin
    fi
fi

bashio::log.info 'Exporter finished successfully. Preparing to stop add-on...'
if bashio::var.has_value "$(bashio::addon.slug)"; then
    bashio::log.info 'Requesting Supervisor to stop this add-on...'
    bashio::addon.stop || bashio::log.warning 'Supervisor stop request failed, exiting manually.'
fi

bashio::log.info '✅ Git Export complete — shutting down now.'
exit 0
