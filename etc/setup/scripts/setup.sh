#! /usr/bin/env bash
set -e

# -- Prerequisites --
echo
echo "- Generating prerequisites; -"

export KC_CLIENT_ID_64=$(echo -n ${KC_CLIENT_ID} | base64)
echo "Generated KC_CLIENT_ID_64 as ${KC_CLIENT_ID_64}"

echo "- Done with prereqs.. -"
# --

echo
echo "Setting up Keycloak;"
source ${PWD}/etc/setup/scripts/subtasks/keycloak_setup.sh


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
echo "-- AuthZ Setup Done! --"
echo
