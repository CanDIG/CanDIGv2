#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

mkdir -p tmp/template
if [[ ! -f "tmp/template/secret-key" ]]; then
    mv tmp/secrets/template-secret-key tmp/template/secret-key
fi

# if we didn't need this temp secret, delete it
if [[ -f "tmp/secrets/template-secret-key" ]]; then
    rm tmp/secrets/template-secret-key
fi
