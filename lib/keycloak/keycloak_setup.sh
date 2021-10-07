#!/usr/bin/env bash

set -Eeuo pipefail

# Verify if keycloak container is running
KEYCLOAK_CONTAINERS=$(echo "$(docker ps | grep keycloak | wc -l)")
echo "Number of keycloak containers running: ${KEYCLOAK_CONTAINERS}"
if [[ $KEYCLOAK_CONTAINERS -eq 0 ]]; then
  echo "Booting keycloak container!"
  export SERVICE=keycloak && make compose-keycloak
  sleep 5
  echo ">> .. waiting for keycloak to start..."
  while ! docker logs --tail 1000 "$(docker ps | grep keycloak | awk '{print $1}')" | grep "Undertow HTTPS listener https listening on 0.0.0.0"; do sleep 1; done
  echo ">> .. ready..."
fi

add_user() {
  # CANDIG_AUTH_DOMAIN is the name of the keycloak server inside the compose network
  local username=$1
  local password=$2

  echo "    Adding user ${username}"
  docker exec ${CANDIG_AUTH_DOMAIN} /opt/jboss/keycloak/bin/add-user-keycloak.sh -u ${username} -p ${password} -r ${KEYCLOAK_REALM}

  echo "    Restarting the keycloak container"
  docker restart ${CANDIG_AUTH_DOMAIN}
}

get_token() {
  local keycloak_admin_user=$(cat tmp/secrets/keycloak-admin-user)
  local keycloak_admin_password=$(cat tmp/secrets/keycloak-admin-password)

  local BID=$(curl \
    -d "client_id=admin-cli" \
    -d "username=${keycloak_admin_user}" \
    -d "password=${keycloak_admin_password}" \
    -d "grant_type=password" \
    "${KEYCLOAK_PUBLIC_URL}/auth/realms/master/protocol/openid-connect/token" -k 2>/dev/null)
    # TODO: security issue fix this, -k flag above ignores cert, even if the url is https

  echo ${BID} | python3 -c 'import json,sys;obj=json.load(sys.stdin);print(obj["access_token"])'
}

set_realm() {
  local realm=$1

  local JSON='{
    "realm": "candig",
    "enabled": true
  }'

  curl \
    -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    -X POST -H "Content-Type: application/json" -d "${JSON}" \
    "${KEYCLOAK_PUBLIC_URL}/auth/admin/realms" -k
}

get_realm() {
  local realm=$1

  curl \
    -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    "${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${realm}" -k | jq .
}

get_realm_clients() {
  local realm=$1

  curl \
    -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    "${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${realm}/clients" -k | jq -S .
}

set_client() {
  local realm=$1
  local client=$2
  local listen=$3
  local redirect=$4

  # Will add / to listen only if it is present

  local JSON='{
    "clientId": "'"${client}"'",
    "enabled": true,
    "protocol": "openid-connect",
    "implicitFlowEnabled": true,
    "standardFlowEnabled": true,
    "publicClient": false,
    "redirectUris": [
      "'${CANDIG_PUBLIC_URL}${redirect}'"
    ],
    "attributes": {
      "saml.assertion.signature": "false",
      "saml.authnstatement": "false",
      "saml.client.signature": "false",
      "saml.encrypt": "false",
      "saml.force.post.binding": "false",
      "saml.multivalued.roles": "false",
      "saml.onetimeuse.condition": "false",
      "saml.server.signature": "false",
      "saml.server.signature.keyinfo.ext": "false",
      "saml_force_name_id_format": "false"
    }
  }'
  echo $JSON
  curl \
    -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    -X POST -H "Content-Type: application/json" -d "${JSON}" \
    "${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${realm}/clients" -k
}

get_secret() {
  id=$(curl -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    ${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${KEYCLOAK_REALM}/clients -k 2>/dev/null |
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print([l["id"] for l in obj if l["clientId"] ==
    "'"$KEYCLOAK_CLIENT_ID"'" ][0])')

  curl -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    ${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${KEYCLOAK_REALM}/clients/$id/client-secret -k 2>/dev/null |
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["value"])'
}

get_public_key() {
  curl \
    ${KEYCLOAK_PUBLIC_URL}/auth/realms/${KEYCLOAK_REALM} -k 2>/dev/null |
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["public_key"])'
}

# SCRIPT START

echo "    Starting setup calls to keycloak"

echo "Getting keycloak token"
KEYCLOAK_TOKEN=$(get_token)

echo "Creating Realm ${KEYCLOAK_REALM}"
set_realm ${KEYCLOAK_REALM}

echo "Setting client ${KEYCLOAK_CLIENT_ID}"
set_client ${KEYCLOAK_REALM} ${KEYCLOAK_CLIENT_ID} "${TYK_LISTEN_PATH}" ${KEYCLOAK_LOGIN_REDIRECT_PATH}

echo "Getting keycloak secret"
KEYCLOAK_SECRET_RESPONSE=$(get_secret ${KEYCLOAK_REALM})
export KEYCLOAK_SECRET=$KEYCLOAK_SECRET_RESPONSE


echo "Getting keycloak public key"
KEYCLOAK_PUBLIC_KEY_RESPONSE=$(get_public_key ${KEYCLOAK_REALM})
export KEYCLOAK_PUBLIC_KEY=$KEYCLOAK_PUBLIC_KEY_RESPONSE
echo "Retrieved keycloak public key as ${KEYCLOAK_PUBLIC_KEY}"

if [[ ${KEYCLOAK_GENERATE_TEST_USER} == 1 ]]; then
  echo "Adding test user"
  add_user "$(cat tmp/secrets/keycloak-test-user)" "$(cat tmp/secrets/keycloak-test-user-password)"
fi

echo "Waiting for keycloak to restart"
while ! docker logs --tail 5 ${CANDIG_AUTH_DOMAIN} | grep "Admin console listening on http://127.0.0.1:9990"; do sleep 1; done
echo "Ready"
