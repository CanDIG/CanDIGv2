#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

bash lib/postgres/restore_db.sh $HTSGET_DB htsget