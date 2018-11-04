#!/usr/bin/env bash

set -xe

if [ ! -d "$(pwd)/mnt/mc" ]; then 
  mkdir -p $(pwd)/mnt/mc/data
fi

if [ ! -d "$(pwd)/etc/mc" ]; then 
  mkdir -p $(pwd)/etc/mc/config
  #cp $(pwd)/mc-sample.config.json $(pwd)/etc/minio/config.json
fi

docker run -it \
  --name=mc_shell \
  -v $(pwd)/mnt/mc/data:/data \
  -v $(pwd)/etc/mc/config:/root/.mc \
  --entrypoint=/bin/sh \
  minio/mc
