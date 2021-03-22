#! /usr/bin/env bash
set -e


# -- Prerequisites --
echo
echo "- Generating prerequisites; -"

mkdir -p ${PWD}/lib/authentication/keycloak
mkdir -p ${PWD}/lib/authentication/tyk

mkdir -p ${PWD}/lib/authorization/vault

export KC_CLIENT_ID_64=$(echo -n ${KC_CLIENT_ID} | base64)
echo "Generated KC_CLIENT_ID_64 as ${KC_CLIENT_ID_64}"

echo "- Done with prereqs.. -"
# --

echo
echo "Setting up Keycloak;"
source ${PWD}/etc/setup/scripts/subtasks/keycloak_setup.sh 
#$1


echo
echo "Setting up Tyk;"
${PWD}/etc/setup/scripts/subtasks/tyk_setup.sh

echo
echo "Setting up Vault;"
source ${PWD}/etc/setup/scripts/subtasks/vault_setup.sh

echo
echo "Setting up OPAs;"
${PWD}/etc/setup/scripts/subtasks/opa_setup.sh

echo
echo "Setting up Arbiters;"
${PWD}/etc/setup/scripts/subtasks/arbiter_setup.sh


echo
echo "Moving temporary files to ./tmp/authorization/*"
mkdir -p ./tmp/configs/authentication
mkdir -p ./tmp/configs/authorization

cp -r ./lib/authentication/keycloak/tmp ./tmp/configs/authentication/keycloak/
cp -r ./lib/authentication/tyk/tmp ./tmp/configs/authentication/tyk/

cp -r ./lib/authorization/vault/tmp ./tmp/configs/authorization/vault/
cp -r ./lib/candig-server/authorization/tmp ./tmp/configs/authorization/candig-server

rm -rf ./lib/authentication/*/tmp 
rm -rf ./lib/authorization/*/tmp 
rm -rf ./lib/candig-server/authorization/tmp 


echo
echo "-- authorization Setup Done! --"
echo
