#!/bin/bash

# Load credentials from secrets
export KEYCLOAK_ADMIN_PASSWORD=$(< /run/secrets/keycloak-admin-password)

if [ "$CANDIG_DEBUG_MODE" = 1 ]; then
  exec /opt/keycloak/bin/kc.sh start-dev
else
  exec /opt/keycloak/bin/kc.sh start
fi