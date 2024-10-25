#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

# if there isn't already a value, store the password in tmp/postgres/db-secret
mkdir -p tmp/postgres
if [[ ! -f "tmp/postgres/db-secret" ]]; then
    mv tmp/secrets/postgres-db-secret tmp/postgres/db-secret
fi

# if we didn't need this temp secret, delete it
if [[ -f "tmp/secrets/postgres-db-secret" ]]; then
    rm tmp/secrets/postgres-db-secret
fi
