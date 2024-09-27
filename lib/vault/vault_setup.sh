#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=tmp/progress.txt

# make sure we have all the env vars:
source env.sh

# this is the name of the ingest service (in case it changes)
ingest="candig-ingest"

# This script runs after the container is composed.

# This script will set up a full vault environment on your local CanDIGv2 cluster

# Automates instructions written at
# https://github.com/CanDIG/CanDIGv2/blob/stable/docs/configure-vault.md

# Related resources:
# https://www.bogotobogo.com/DevOps/Docker/Docker-Vault-Consul.php
# https://learn.hashicorp.com/tutorials/vault/identity
# https://stackoverflow.com/questions/35703317/docker-exec-write-text-to-file-in-container
# https://www.vaultproject.io/api-docs/secret/identity/entity#batch-delete-entities

vault=$(docker ps -a --format "{{.Names}}" | grep vault_1 | awk '{print $1}')
vault_runner=$(docker ps -a --format "{{.Names}}" | grep vault-runner_1 | awk '{print $1}')

docker cp lib/vault/tmp/vault-config.json $vault:/vault/config/


# check to see if we need to restore a backup before initializing a fresh Vault:
if [[ -f "lib/vault/restore.tar.gz" ]]; then
  echo ">> restoring vault from backup"
  docker stop $vault
  pwd=$(pwd)
  cd lib/vault/tmp
  tar -xzf $pwd/lib/vault/restore.tar.gz
  cd $pwd
  cp lib/vault/tmp/backup/keys.txt tmp/vault/
  docker cp lib/vault/tmp/backup/keys.txt $vault_runner:/vault/config/
  docker cp lib/vault/tmp/backup/backup.tar.gz $vault_runner:/vault/
  docker exec $vault_runner bash -c "cd /vault; tar -xzf backup.tar.gz"
  rm -R lib/vault/tmp/backup
  mv lib/vault/restore.tar.gz lib/vault/restored.tar.gz
fi

# if vault isn't started, start it:
docker restart $vault

echo ">> waiting for vault to start"
docker ps --format "{{.Names}}" | grep vault_1
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  docker ps --format "{{.Names}}" | grep vault_1
done
sleep 10

# gather keys and login token
stuff=$(docker exec $vault vault operator init) # | head -7 | rev | cut -d " " -f1 | rev)
if [[ $? -eq 0 ]]; then
  echo ">> initialized vault, saving keys"

  key_1=$(echo -n "${stuff}" | grep 'Unseal Key 1: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
  key_2=$(echo -n "${stuff}" | grep 'Unseal Key 2: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
  key_3=$(echo -n "${stuff}" | grep 'Unseal Key 3: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
  key_4=$(echo -n "${stuff}" | grep 'Unseal Key 4: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
  key_5=$(echo -n "${stuff}" | grep 'Unseal Key 5: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
  key_root=$(echo -n "${stuff}" | grep 'Initial Root Token: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')

  echo "found key1: ${key_1}"
  echo "found key2: ${key_2}"
  echo "found key3: ${key_3}"
  echo "found key4: ${key_4}"
  echo "found key5: ${key_5}"
  echo "found root: ${key_root}"

  # save keys
  touch tmp/vault/keys.txt
  echo -e "keys: \n${key_1}" > tmp/vault/keys.txt
  echo -e "${key_2}" >> tmp/vault/keys.txt
  echo -e "${key_3}" >> tmp/vault/keys.txt
  echo -e "${key_4}" >> tmp/vault/keys.txt
  echo -e "${key_5}" >> tmp/vault/keys.txt
  echo -e "root: \n${key_root}" >> tmp/vault/keys.txt

  docker cp tmp/vault/keys.txt $vault:/vault/config/

else
  echo ">> retrieving keys"
  key_1=$(head -n 2 tmp/vault/keys.txt | tail -n 1)
  key_2=$(head -n 3 tmp/vault/keys.txt | tail -n 1)
  key_3=$(head -n 4 tmp/vault/keys.txt | tail -n 1)

  key_root=$(tail -n 1 tmp/vault/keys.txt)
fi
echo $key_root
echo ">> attempting to automatically unseal vault:"
docker exec $vault sh -c "vault operator unseal ${key_1}"
docker exec $vault sh -c "vault operator unseal ${key_2}"
docker exec $vault sh -c "vault operator unseal ${key_3}"

# login
echo
echo ">> logging in automatically -- " #copy and paste this: ${key_root}"
docker exec $vault sh -c "vault login ${key_root}"

# configuration
# audit file
echo
echo ">> enabling audit file"
docker exec $vault sh -c "vault audit enable file file_path=/vault/vault-audit.log"

# enable approle
echo
echo ">> enabling approle"
docker exec $vault sh -c "vault auth enable approle"

echo ">> setting up approle policy"
docker exec $vault sh -c "echo 'path \"auth/approle/role/*\" {capabilities = [\"create\", \"update\", \"read\", \"delete\"]}' > approle-policy.hcl; vault policy write approle approle-policy.hcl"

echo
echo ">> setting up approle role"
cidr_block=$(docker network inspect --format "{{json .IPAM.Config}}" candigv2_default | jq '.[0].Gateway')
cidr_block=$(echo ${cidr_block} | tr -d '"')
cidr_block="${cidr_block}/27"
if [ $CANDIG_DEBUG_MODE -eq 1 ]; then
  echo "{}" > lib/vault/tmp/temp.json
else
  echo "{\"bound_cidrs\": [\"${cidr_block}\"]}" > lib/vault/tmp/temp.json
fi
curl --request POST --header "X-Vault-Token: ${key_root}" --data @lib/vault/tmp/temp.json $VAULT_SERVICE_PUBLIC_URL/v1/auth/token/roles/approle
rm lib/vault/tmp/temp.json

echo
echo ">> setting up approle token"
approle_token=$(cat tmp/vault/approle-token)
echo "{\"id\": \"${approle_token}\", \"policies\": [\"approle\"], \"periodic\": \"24h\"}" > lib/vault/tmp/temp.json
curl --request POST --header "X-Vault-Token: ${key_root}" --data @lib/vault/tmp/temp.json $VAULT_SERVICE_PUBLIC_URL/v1/auth/token/create/approle
rm lib/vault/tmp/temp.json

# Containers need to access the client secret and id:
docker exec $vault vault secrets enable -path=keycloak -description="keycloak kv store" kv

curl --request POST --header "X-Vault-Token: ${key_root}" --data "{\"value\": \"$CANDIG_CLIENT_SECRET\"}" $VAULT_SERVICE_PUBLIC_URL/v1/keycloak/client-secret

curl --request POST --header "X-Vault-Token: ${key_root}" --data "{\"value\": \"$CANDIG_CLIENT_ID\"}" $VAULT_SERVICE_PUBLIC_URL/v1/keycloak/client-id

## SPECIAL STORES ACCESS
# Ingest needs access to the opa store's programs path:
docker exec $vault sh -c "echo 'path \"opa/programs\" {capabilities = [\"update\", \"read\"]}' >> ${ingest}-policy.hcl; echo 'path \"opa/programs/*\" {capabilities = [\"create\", \"update\", \"read\", \"delete\"]}' >> ${ingest}-policy.hcl; echo 'path \"opa/site_roles\" {capabilities = [\"create\", \"update\", \"read\", \"delete\"]}' >> ${ingest}-policy.hcl; echo 'path \"opa/users/*\" {capabilities = [\"create\", \"update\", \"read\", \"delete\"]}' >> ${ingest}-policy.hcl; echo 'path \"opa/pending_users\" {capabilities = [ \"update\", \"read\"]}' >> ${ingest}-policy.hcl; vault policy write ${ingest} ${ingest}-policy.hcl"

# Federation needs access to the opa store's data path (to add servers):
docker exec $vault sh -c "echo 'path \"opa/data\" {capabilities = [\"update\", \"read\", \"delete\"]}' >> federation-policy.hcl; vault policy write federation federation-policy.hcl"

# Htsget needs access to the ingest store's aws path:
docker exec $vault sh -c "echo 'path \"candig-ingest/aws/*\" {capabilities = [\"read\"]}' >> htsget-policy.hcl; vault policy write htsget htsget-policy.hcl"

docker restart $vault_runner

if [ -f tmp/vault/service_stores.txt ]; then
    echo ">> creating service stores"
    while read service; do
        bash create_service_store.sh $service
    done <tmp/vault/service_stores.txt
fi
