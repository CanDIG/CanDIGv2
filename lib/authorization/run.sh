#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
  source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
  conda activate ${VENV_NAME}

pushd $(pwd)/lib/fauthorization/candig_authz_service/
  pip install -r requirements.txt
  pip install git+https://github.com/candig/candig_authz_service.git
  candig_authz_service --host ${AUTHORIZATION_SERVICE_HOST} --port ${AUTHORIZATION_SERVICE_PORT}
popd
