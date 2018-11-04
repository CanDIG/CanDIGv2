#!/usr/bin/env bash

set -xe

docker run \
  -p 9000:9000 \
  --name minio1 \
  -v $(pwd)/mnt/minio1/data:/data \
  -v $(pwd)/mnt/minio1/config:/root/.minio \
  minio/minio server /data
