#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

pushd $(pwd)/lib/htsget-server/htsget_app
	python setup.py install
	python htsget_server/server.py
popd
