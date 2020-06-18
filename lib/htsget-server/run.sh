#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
  source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
  conda activate ${VENV_NAME}

pushd $(pwd)/lib/htsget-server/htsget_app
  pip install -r requirements.txt
  python setup.py install
  python htsget_server/server.py
popd
