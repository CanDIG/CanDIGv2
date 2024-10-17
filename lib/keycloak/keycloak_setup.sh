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
KEYCLOAK_ADMIN=${DEFAULT_ADMIN_USER}
KEYCLOAK_ADMIN_PASSWORD=$(cat tmp/keycloak/admin-password)
READY_CHECK_URL="${KEYCLOAK_PUBLIC_URL}/auth/health/ready"
KC_ADMIN_URL="${KEYCLOAK_PUBLIC_URL}/auth"
DEBUG_MODE=false
#####################################################

echo -e "🚧🚧🚧 ${YELLOW}KEYCLOAK SETUP BEGIN${DEFAULT} 🚧🚧🚧"
echo -n ">> waiting for keycloak to start"

function READY_CHECK() {
    if [ "$DEBUG_MODE" = true ]; then
        curl --head -fsS "${READY_CHECK_URL}" | grep -q "200"
    else
        curl --head -s "${READY_CHECK_URL}" | grep -q "200"
    fi
}

until READY_CHECK; do
    printf '.'
    sleep 1
done

echo -e "\n${GREEN}Keycloak is ready ✅${DEFAULT}"

# Get the Keycloak container ID
KEYCLOAK_CONTAINER_ID=$(docker ps | grep keycloak/keycloak | awk '{print $1}')

# Define the KCADM function to run commands inside the Keycloak container
function KCADM() {
    local show_output=false
    if [ "$1" = "-full" ]; then
        show_output=true
        shift
    fi

    if [ "$DEBUG_MODE" = true ]; then
        docker exec "$KEYCLOAK_CONTAINER_ID" /opt/keycloak/bin/kcadm.sh "$@" || handle_error
    else
        if [ "$show_output" = true ]; then
            docker exec "$KEYCLOAK_CONTAINER_ID" /opt/keycloak/bin/kcadm.sh "$@" || handle_error
        else
            docker exec "$KEYCLOAK_CONTAINER_ID" /opt/keycloak/bin/kcadm.sh "$@" > /dev/null 2>&1 || handle_error
        fi
    fi
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

# copy custom theming
docker cp lib/keycloak/theme/keycloak candigv2_keycloak_1:/opt/keycloak/themes/
KCADM update realms/candig -s "loginTheme=keycloak"

echo -e "🎉🎉🎉 ${GREEN}KEYCLOAK SETUP DONE!${DEFAULT} 🎉🎉🎉"
