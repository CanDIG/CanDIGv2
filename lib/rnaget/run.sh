#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
  source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
  conda activate ${VENV_NAME}

pushd $(pwd)/lib/rnaget/rnaget_service/
  pip install -r requirements.txt
  python setup.py develop

  candig_rnaget --host=${RNA_GET_HOST} --port=${RNA_GET_PORT}
popd
