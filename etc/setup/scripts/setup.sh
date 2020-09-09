# -- Prerequisites --
echo
echo "- Generating Prerequisites; -"
export KC_CLIENT_ID_64=$(echo -n ${KC_CLIENT_ID} | base64)
echo "Generated KC_CLIENT_ID_64 as ${KC_CLIENT_ID_64}"

## Todo: 
## export KC_SECRET
## echo "Generated KC_SECRET as ${KC_SECRET}"
echo "- Prereqs. Done -"
# --

echo "Setting up Tyk"
${PWD}/etc/setup/scripts/subtasks/tyk_setup.sh

#echo "Setting up Keycloak"
#./subtasks/keycloak_setup.sh

#echo "Setting up Vault"
#./subtasks/vault_setup.sh
