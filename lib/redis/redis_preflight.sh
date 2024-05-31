#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

# if there isn't already a value, store the password in tmp/redis/secret-key
if [[ ! -f "tmp/redis/secret-key" ]]; then
    mv tmp/secrets/redis-secret-key tmp/redis/secret-key
fi

# if we didn't need this temp secret, delete it
if [[ -f "tmp/secrets/redis-secret-key" ]]; then
    rm tmp/secrets/redis-secret-key
fi
