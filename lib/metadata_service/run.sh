#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

pushd $(pwd)/lib/metadata_service/metadata_service_v2
	pip install -r requirements.txt
    ./manage.py runserver $METADATA_SERVICE_IP:$METADATA_SERVICE_PORT
popd
