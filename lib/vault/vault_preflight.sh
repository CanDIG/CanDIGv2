#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=tmp/progress.txt

# This script runs before the container is composed.

mkdir -p lib/vault/tmp

# vault-config.json
echo "Working on vault-config.json .."
envsubst < lib/vault/configuration_templates/vault-config.json.tpl > lib/vault/tmp/vault-config.json

# if there isn't already a value, store the value in tmp/vault/approle-token
mkdir -p tmp/vault
if [[ ! -f "tmp/vault/approle-token" ]]; then
    mv tmp/secrets/vault-approle-token tmp/vault/approle-token
fi

# if we didn't need this temp secret, delete it
if [[ -f "tmp/secrets/vault-approle-token" ]]; then
    rm tmp/secrets/vault-approle-token
fi
