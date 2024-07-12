#!/bin/bash

# Load credentials from secrets
export KEYCLOAK_ADMIN_PASSWORD=$(< /run/secrets/keycloak-admin-password)

if [ "$CANDIG_PRODUCTION_MODE" = 1 ]; then
  exec /opt/keycloak/bin/kc.sh start
else
  exec /opt/keycloak/bin/kc.sh start-dev
fi