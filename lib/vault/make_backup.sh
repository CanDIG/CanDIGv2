#!/usr/bin/env bash

vault=$(docker ps -a --format "{{.Names}}" | grep vault_1 | awk '{print $1}')
vault_runner=$(docker ps -a --format "{{.Names}}" | grep vault-runner_1 | awk '{print $1}')

mkdir -p $(pwd)/tmp/vault/backup
stop=$(docker stop $vault)
zip=$(docker exec $vault_runner bash -c "cd /vault; tar -cz data/ > backup.tar.gz")
copy=$(docker cp $vault_runner:/vault/backup.tar.gz $(pwd)/tmp/vault/backup/)

cp $(pwd)/tmp/vault/keys.txt $(pwd)/tmp/vault/backup
pwd=$(pwd)
cd $(pwd)/tmp/vault
tar -cz backup > backup.tar.gz
rm -R backup
cd $pwd

start=$(docker start $vault)
