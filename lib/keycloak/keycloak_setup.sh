#!/usr/bin/env bash

# Entrypoint into Keycloak. It uses Keycloak Admin CLI (KCADM)
# to setup realms, clients, and users for candig services.

set -euo pipefail

# Terminal colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
DEFAULT='\033[0m'

handle_error() {
    echo -e "🚨🚨🚨 ${RED}AN ERROR OCCURRED DURING KEYCLOAK SETUP PROCESS${DEFAULT} 🚨🚨🚨"
    exit 1
}

# Trap ERR signal to call handle_error function
trap handle_error ERR

####################################################
#              VARIABLES CONFIGURATION             #
####################################################
KEYCLOAK_ADMIN=$(cat tmp/secrets/keycloak-admin-user)
KEYCLOAK_ADMIN_PASSWORD=$(cat tmp/secrets/keycloak-admin-password)
READY_CHECK_URL="http://${CANDIG_DOMAIN}:${KEYCLOAK_PORT}/auth/health/ready"
# KC_ADMIN_URL="http://host.docker.internal:8080/auth"
KC_ADMIN_URL="http://${CANDIG_DOMAIN}:${KEYCLOAK_PORT}/auth"
#####################################################

echo -e "🚧🚧🚧 ${YELLOW}KEYCLOAK SETUP BEGIN${DEFAULT} 🚧🚧🚧"
echo -n ">> waiting for keycloak to start"
# keycloak is booting up before it can accept any requests
until $(curl --output /dev/null --silent --fail --head "${READY_CHECK_URL}"); do
    printf '.'
    sleep 1
done
echo -e "\n${GREEN}Keycloak is ready ✅${DEFAULT}"

# Get the Keycloak container ID
KEYCLOAK_CONTAINER_ID=$(docker ps | grep keycloak/keycloak | awk '{print $1}')

# Define the KCADM function to run commands inside the Keycloak container
function KCADM() {
    docker exec "$KEYCLOAK_CONTAINER_ID" /opt/keycloak/bin/kcadm.sh "$@"
}

# authenticate as admin
KCADM config credentials --server $KC_ADMIN_URL --user $KEYCLOAK_ADMIN --password $KEYCLOAK_ADMIN_PASSWORD --realm master

# create realm
source ./lib/keycloak/realm_setup.sh
# create client
source ./lib/keycloak/client_setup.sh
# create test users
if [ "${KEYCLOAK_GENERATE_TEST_USER}" == "1" ]; then
    source ./lib/keycloak/user_setup.sh
fi

echo -e "🎉🎉🎉 ${GREEN}KEYCLOAK SETUP DONE!${DEFAULT} 🎉🎉🎉"
