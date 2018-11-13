#!/bin/bash

#!/usr/bin/env bash

set -xe

if [ ! -d "./etc/trafik" ]; then
  mkdir -p ./etc/trafik/{config,data}
fi

docker network create \
    --driver overlay \
    --attachable \
    traefik_net

docker stack deploy --compose-file ./lib/traefik/traefik-net.yml traefik
