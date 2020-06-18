#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
  source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
  conda activate ${VENV_NAME}

pushd $(pwd)/lib/cnv_service/candig_cnv_service
  python setup.py install
  candig_cnv_service --host ${CNV_SERVICE_HOST} --port ${CNV_SERVICE_PORT}
popd
