#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

pushd $(pwd)/lib/federation-service/federation_service
    # Using another enviroment in order to avoid packages conflict
    python3 -m venv federation_service_venv
    source federation_service_venv/bin/activate
    pip install -r requirements.txt
    python -m candig_federation --host ${FEDERATION_SERVICE_IP} --port ${FEDERATION_SERVICE_PORT}
popd
