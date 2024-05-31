#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

# if there isn't already a value, store the password in tmp/postgres/db-secret
if [[ ! -f "tmp/postgres/db-secret" ]]; then
    mv tmp/secrets/metadata-db-secret tmp/postgres/db-secret
fi

# if we didn't need this temp secret, delete it
if [[ -f "tmp/secrets/metadata-db-secret" ]]; then
    rm tmp/secrets/metadata-db-secret
fi
