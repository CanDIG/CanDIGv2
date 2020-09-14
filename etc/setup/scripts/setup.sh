#! /bin/bash
# -- Prerequisites --
echo
echo "- Generating prerequisites; -"

export KC_CLIENT_ID_64=$(echo -n ${KC_CLIENT_ID} | base64)
echo "Generated KC_CLIENT_ID_64 as ${KC_CLIENT_ID_64}"

echo "- Done with prereqs.. -"
echo
# --

echo "Setting up Keycloak"
${PWD}/etc/setup/scripts/subtasks/keycloak_setup.sh

#echo "Setting up Tyk"
#${PWD}/etc/setup/scripts/subtasks/tyk_setup.sh

#echo "Setting up Vault"
#${PWD}/etc/setup/scripts/subtasks/vault_setup.sh
