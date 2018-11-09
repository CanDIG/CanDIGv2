#!/usr/bin/env bash

set -xe

if [ ! -d "./etc/mc" ]; then
  mkdir -p ./etc/mc/{config,data}
  #cp ./lib/mc/sample.config.json ./etc/mc/config/config.json
fi

if [ -f "./minio_secret_key" ]; then
  access_key=$(cat minio_access_key)
  secret_key=$(cat minio_secret_key)
else
  echo "WARNING: no credentials file found, configure mc shell manually!"
fi

docker run -it \
  --name=mc_shell \
  -v ./etc/mc/data:/data \
  -v ./etc/mc/config:/root/.mc \
  --entrypoint=/bin/sh \
  minio/mc

#docker exec -it  mc_shell mc config host add candig http://172.17.0.2:9000 $access_key $secret_key
