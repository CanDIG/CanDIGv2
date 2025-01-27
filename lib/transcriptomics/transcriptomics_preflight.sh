#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

# copy folder to the transcriptomics container
mkdir -p $PWD/lib/transcriptomics/transcriptomics/lib/
cp -r $PWD/lib/transcriptomics/opa_plugin/* $PWD/lib/transcriptomics/transcriptomics/lib/
cp -r $PWD/lib/transcriptomics/create_db.sh $PWD/lib/transcriptomics/transcriptomics/
cp -r $PWD/lib/transcriptomics/run.bash $PWD/lib/transcriptomics/transcriptomics/
cp -r $PWD/lib/transcriptomics/Dockerfile $PWD/lib/transcriptomics/transcriptomics/