#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

pushd $(pwd)/lib/cnv_service/candig_cnv_service
    python setup.py install
    candig_cnv_service --host ${CNV_SERVICE_HOST} --port ${CNV_SERVICE_PORT}
popd
