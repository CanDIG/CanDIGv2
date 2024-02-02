#!/usr/bin/env bash

set -Euo pipefail


if [[ -f "initial_setup" ]]; then
    cp -R /app/* /vault
    mkdir /vault/data
    chmod 777 /vault/data

    rm initial_setup
else
    sleep 10
    # unseal vault
    KEY=$(head -n 2 /vault/config/keys.txt | tail -n 1)
    echo '{ "key": "'$KEY'" }' > payload.json
    curl --request POST --data @payload.json http://vault:8200/v1/sys/unseal
    KEY=$(head -n 3 /vault/config/keys.txt | tail -n 1)
    echo '{ "key": "'$KEY'" }' > payload.json
    curl --request POST --data @payload.json http://vault:8200/v1/sys/unseal
    KEY=$(head -n 4 /vault/config/keys.txt | tail -n 1)
    echo '{ "key": "'$KEY'" }' > payload.json
    curl --request POST --data @payload.json http://vault:8200/v1/sys/unseal

fi

while [ 0 -eq 0 ]
do
  bash /vault/renew_token.sh
  sleep 600
done
