#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

pushd $(pwd)/lib/federation-service/federation_service
    pip install -r requirements.txt
    python -m candig_federation --port 4232
popd
