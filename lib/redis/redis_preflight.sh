#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

# store the password in tmp/postgres/db-secret
mv tmp/secrets/redis-secret-key tmp/redis/secret-key