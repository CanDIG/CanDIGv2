#!/usr/bin/env bash

set -xe

docker rm -v $(docker ps -aq)

rm -rf $(pwd)/mnt \
  $(pwd)/etc
