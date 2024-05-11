#!/bin/bash

# Load credentials from secrets
export KEYCLOAK_ADMIN_PASSWORD=$(< /run/secrets/keycloak-admin-password)

exec /opt/keycloak/bin/kc.sh "$@"