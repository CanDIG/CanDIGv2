#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
	source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
	conda activate ${VENV_NAME}

mkdir -p $(pwd)/tmp/${MINIO_DATA_DIR}

export MINIO_ACCESS_KEY=`cat $(pwd)/minio-access-key`
export MINIO_SECRET_KEY=`cat $(pwd)/minio-secret-key`
#export MINIO_ACCESS_KEY_FILE=$(pwd)/minio-access-key
#export MINIO_SECRET_KEY_FILE=$(pwd)/minio-secret-key
export MINIO_REGION=${MINIO_REGION}

$(pwd)/bin/minio --address "${MINIO_URL}" server $(pwd)/tmp/${MINIO_DATA_DIR}
