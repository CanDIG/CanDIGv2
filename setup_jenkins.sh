#!/usr/bin/env bash

cp etc/env/example.env .env

grep -q "finished init-conda" $WORKING_DIR/progress.txt
if [ $? -ne 0 ]; then
  echo "need to re-run setup"
  rm $WORKING_DIR/progress.txt
  make bin-all
  make init-conda
  . $PWD/bin/miniconda3/etc/profile.d/conda.sh
  conda activate candig
  pip install -U -r $PWD/etc/venv/requirements.txt
else
  echo "already set up"
fi
