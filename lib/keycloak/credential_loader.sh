#!/bin/bash

if [ "$KEYCLOAK_PROXY_HEADERS" != "none" ]; then
  export cli_settings="--proxy-headers=$KEYCLOAK_PROXY_HEADERS"
fi

# Load credentials from secrets
export KEYCLOAK_ADMIN_PASSWORD=$(< /run/secrets/keycloak-admin-password)

if [ "$CANDIG_PRODUCTION_MODE" = 1 ]; then
  exec /opt/keycloak/bin/kc.sh start $cli_settings
else
  exec /opt/keycloak/bin/kc.sh start-dev
fi