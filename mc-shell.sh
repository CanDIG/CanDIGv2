#!/usr/bin/env bash

set -xe

if [ ! -d "$(pwd)/etc/mc" ]; then 
  mkdir -p $(pwd)/etc/mc/{config,data}
  #cp $(pwd)/lib/mc/sample.config.json $(pwd)/etc/mc/config/config.json
fi

docker run -it \
  --name=mc_shell \
  -v $(pwd)/etc/mc/data:/data \
  -v $(pwd)/etc/mc/config:/root/.mc \
  --entrypoint=/bin/sh \
  minio/mc
