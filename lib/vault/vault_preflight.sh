#!/usr/bin/env bash

set -Eeuo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

mkdir -p ${PWD}/lib/vault/tmp

# vault-config.json
echo "Working on vault-config.json .."
envsubst < ${PWD}/lib/vault/configuration_templates/vault-config.json.tpl > ${PWD}/lib/vault/tmp/vault-config.json
