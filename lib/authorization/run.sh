#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

pushd $(pwd)/lib/fauthorization/candig_authz_service/
    pip install -r requirements.txt
    pip install git+https://github.com/candig/candig_authz_service.git
    candig_authz_service --host ${AUTHORIZATION_SERVICE_HOST} --port ${AUTHORIZATION_SERVICE_PORT}
popd
