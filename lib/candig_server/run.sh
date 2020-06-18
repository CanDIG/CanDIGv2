#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
  source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
  conda activate ${VENV_NAME}

pushd $(pwd)/lib/candig_server/
  pip install candig-server==1.3.0
  pip install candig-ingest==1.3.1
  # Uncomment below lines if you want to ingest some mock data
  # mkdir candig-example-data
  # wget https://raw.githubusercontent.com/CanDIG/candig-ingest/master/candig/ingest/mock_data/clinical_metadata_tier1.json
  # wget https://raw.githubusercontent.com/CanDIG/candig-ingest/master/candig/ingest/mock_data/clinical_metadata_tier2.json
  # ingest candig-example-data/registry.db mock1 clinical_metadata_tier1.json
  # ingest candig-example-data/registry.db mock2 clinical_metadata_tier2.json

  candig_server --host ${CANDIG_SERVER_HOST} --port ${CANDIG_SERVER_PORT}
popd
