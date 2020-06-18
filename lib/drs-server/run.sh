#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
	source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
	conda activate ${VENV_NAME}

export MINIO_USERNAME=<($(pwd)/minio-access-key)
export MINIO_PASSWORD=<($(pwd)/minio-secret-key)

pushd $(pwd)/lib/drs-server/chord_drs
	pip install -r requirements.txt
	flask db upgrade
	flask run --host 0.0.0.0 --port ${CHORD_DRS_PORT}
popd
