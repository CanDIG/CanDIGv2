#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=tmp/progress.txt

# This script runs before the container is composed.

mkdir -p lib/vault/tmp

# vault-config.json
echo "Working on vault-config.json .."
envsubst < lib/vault/configuration_templates/vault-config.json.tpl > lib/vault/tmp/vault-config.json
