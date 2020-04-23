#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

pushd $(pwd)/lib/drs-server/chord_drs
	pip install -r requirements.txt
	flask db upgrade
	flask run --host 0.0.0.0 --port ${CHORD_DRS_PORT}
popd
