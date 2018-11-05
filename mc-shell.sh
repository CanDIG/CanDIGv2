#!/usr/bin/env bash

set -xe

if [ ! -d "$(pwd)/etc/mc" ]; then
  mkdir -p $(pwd)/etc/mc/{config,data}
  #cp $(pwd)/lib/mc/sample.config.json $(pwd)/etc/mc/config/config.json
fi

if [ -f "$(pwd)/credentials" ]; then
  access_key=$(sed -n 1p credentials)
  secret_key=$(sed -n 2p credentials)
else
  echo "WARNING: no credentials file found, configure mc shell manually!"
fi

docker run -it \
  --name=mc_shell \
  -v $(pwd)/etc/mc/data:/data \
  -v $(pwd)/etc/mc/config:/root/.mc \
  --entrypoint=/bin/sh \
  minio/mc

#docker exec -it  mc_shell mc config host add candig http://172.17.0.2:9000 $access_key $secret_key
