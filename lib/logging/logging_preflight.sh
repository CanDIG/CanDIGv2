#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

mkdir -m=$DIR_PERMISSIONS -p tmp/logs
chmod a+w tmp/logs
