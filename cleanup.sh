#!/usr/bin/env bash

set -xe

docker rm -v $(docker ps -aq)

sudo rm -rf $(pwd)/mnt \
  $(pwd)/etc
