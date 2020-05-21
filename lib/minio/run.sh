#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && echo 'Conda ENV not active!' && exit 1

mkdir -p $(pwd)/data

export MINIO_ACCESS_KEY_FILE=$(pwd)/minio-access-key
export MINIO_SECRET_KEY_FILE=$(pwd)/minio-secret-key

export MINIO_ACCESS_KEY=`cat $(pwd)/minio-access-key`
export MINIO_SECRET_KEY=`cat $(pwd)/minio-secret-key`

$(pwd)/bin/minio server $(pwd)/data
