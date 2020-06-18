#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
  source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
  conda activate ${VENV_NAME}

pushd $(pwd)/lib/metadata_service/metadata_service_v2
  pip install -r requirements.txt
  ./manage.py runserver $METADATA_SERVICE_IP:$METADATA_SERVICE_PORT
popd
