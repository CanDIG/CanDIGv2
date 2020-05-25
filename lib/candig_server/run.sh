#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

pushd $(pwd)/lib/candig_server/
    pip install candig-server
    pip install candig-ingest==1.3.1
    mkdir candig-example-data
    wget https://raw.githubusercontent.com/CanDIG/candig-ingest/master/candig/ingest/mock_data/clinical_metadata_tier1.json
    wget https://raw.githubusercontent.com/CanDIG/candig-ingest/master/candig/ingest/mock_data/clinical_metadata_tier2.json
    ingest candig-example-data/registry.db mock1 clinical_metadata_tier1.json
    ingest candig-example-data/registry.db mock2 clinical_metadata_tier2.json

    candig_server --host ${CANDIG_SERVER_HOST} --port ${CANDIG_SERVER_PORT}
popd