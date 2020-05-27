#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

pushd $(pwd)/lib/rnaget/rnaget_service/
    pip install -r requirements.txt
    python setup.py develop

    candig_rnaget --host=${RNA_GET_HOST} --port=${RNA_GET_PORT}
popd