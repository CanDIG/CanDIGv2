#!/bin/bash
password=$(cat ../../tmp/secrets/keycloak-test-user2-password)
client_secret=$(cat ../..tmp/secrets/keycloak-client-local_candig-secret)
curl -X "POST" "http://candig.docker.internal:8080/auth/realms/candig/protocol/openid-connect/token" \
     -H 'Content-Type: application/x-www-form-urlencoded; charset=utf-8' \
     --data-urlencode "client_id=local_candig" \
     --data-urlencode "client_secret=${client_secret}" \
     --data-urlencode "grant_type=password" \
     --data-urlencode "username=user2" \
     --data-urlencode "password=${password}" \
     --data-urlencode "scope=openid"