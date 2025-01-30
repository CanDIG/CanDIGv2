#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

# copy folder to the rnaget container
mkdir -p $PWD/lib/rnaget/rnaget/lib/
cp -r $PWD/lib/rnaget/opa_plugin/* $PWD/lib/rnaget/rnaget/lib/
cp -r $PWD/lib/rnaget/create_db.sh $PWD/lib/rnaget/rnaget/
cp -r $PWD/lib/rnaget/run.bash $PWD/lib/rnaget/rnaget/
cp -r $PWD/lib/rnaget/Dockerfile $PWD/lib/rnaget/rnaget/