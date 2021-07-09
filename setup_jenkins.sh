#!/usr/bin/env bash

LOGFILE=$PWD/tmp/logs/progress.txt

sed 's/DOCKER_REGISTRY=.*/DOCKER_REGISTRY=ghcr.io\/candig/' etc/env/example.env > .env

# grep -q "finished init-conda" $LOGFILE
. $PWD/bin/miniconda3/etc/profile.d/conda.sh
conda activate candig
if [ $? -ne 0 ]; then
  echo "need to re-run setup"
  rm $LOGFILE
  make bin-all
  make init-conda
  . $PWD/bin/miniconda3/etc/profile.d/conda.sh
  conda activate candig
  pip install -U -r $PWD/etc/venv/requirements.txt
else
  echo "already set up"
fi
