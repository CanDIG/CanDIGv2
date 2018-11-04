#!/usr/bin/env bash

docker run -it \
  --name=mc_shell \
  -v $(pwd)/mnt/mc/config:/root/.mc \
  -v $(pwd)/mnt/mc/data:/data
  --entrypoint=/bin/sh \
  minio/mc
