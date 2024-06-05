#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

# if there isn't already a value, store the passwords in tmp/keycloak
if [[ ! -f "tmp/keycloak/admin-password" ]]; then
    mv tmp/secrets/keycloak-admin-password tmp/keycloak/admin-password
fi
if [[ ! -f "tmp/keycloak/client-secret" ]]; then
    mv tmp/secrets/keycloak-client-secret tmp/keycloak/client-secret
fi
if [[ ! -f "tmp/keycloak/keycloak-test-site-admin-password" ]]; then
    mv tmp/secrets/keycloak-test-site-admin-password tmp/keycloak/test-site-admin-password
fi
if [[ ! -f "tmp/keycloak/keycloak-test-user-password" ]]; then
    mv tmp/secrets/keycloak-test-user-password tmp/keycloak/test-user-password
fi
if [[ ! -f "tmp/keycloak/keycloak-test-user2-password" ]]; then
    mv tmp/secrets/keycloak-test-user2-password tmp/keycloak/test-user2-password
fi

# if we didn't need these temp secrets, delete them
if [[ -f "tmp/secrets/keycloak-admin-password" ]]; then
    rm tmp/secrets/keycloak-admin-password
fi
if [[ -f "tmp/secrets/keycloak-client-secret" ]]; then
    rm tmp/secrets/keycloak-client-secret
fi
if [[ -f "tmp/secrets/keycloak-test-site-admin-password" ]]; then
    rm tmp/secrets/keycloak-test-site-admin-password
fi
if [[ -f "tmp/secrets/keycloak-test-user-password" ]]; then
    rm tmp/secrets/keycloak-test-user-password
fi
if [[ -f "tmp/secrets/keycloak-test-user2-password" ]]; then
    rm tmp/secrets/keycloak-test-user2-password
fi
