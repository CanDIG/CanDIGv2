#!/usr/bin/env bash

set -Eeuo pipefail

LOGFILE=$PWD/tmp/progress.txt


# Verify if keycloak container is running
KEYCLOAK_CONTAINERS=$(echo "$(docker ps | grep keycloak | wc -l)")
echo "Number of keycloak containers running: ${KEYCLOAK_CONTAINERS}" | tee -a $LOGFILE
if [[ $KEYCLOAK_CONTAINERS -eq 0 ]]; then
  echo "Booting keycloak container!" | tee -a $LOGFILE
  make compose-keycloak
  sleep 5
  echo "Waiting for keycloak to start" | tee -a $LOGFILE
  while ! docker logs --tail 1000 "$(docker ps | grep keycloak | awk '{print $1}')" | grep "Undertow HTTPS listener https listening on 0.0.0.0"; do sleep 1; done
  echo "Keycloak container started." | tee -a $LOGFILE
fi

add_user() {
  # CANDIG_AUTH_DOMAIN is the name of the keycloak server inside the compose network
  local username=$1
  local password=$2
  local attribute=$3

  local JSON='  {
    "username": "'${username}'",
    "enabled": true,
    "attributes": {
      "'${attribute}'": [
        "true"
      ]
    },
    "access": {
      "manageGroupMembership": true,
      "view": true,
      "mapRoles": true,
      "impersonate": true,
      "manage": true
    }
  }'

  user_id=`curl --stderr - \
    -i -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    -X POST -H "Content-Type: application/json" -d "${JSON}" \
    "${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${KEYCLOAK_REALM}/users" -k | grep "Location:" \
    | sed -E s/.*users.\([a-z0-9-]+\).*/\\\1/`

  echo "Created user ${user_id}" | tee -a $LOGFILE

  local password_json=' {
    "type": "rawPassword",
    "value": "'${password}'"
  }'
  echo "${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${KEYCLOAK_REALM}/users/${user_id}"
  curl \
    -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    -X PUT -H "Content-Type: application/json" -d "${password_json}" \
    "${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${KEYCLOAK_REALM}/users/${user_id}/reset-password" -k
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
    "realm": "'${realm}'",
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
  local redirect=$3

  # add client scope with protocol mappers
  scope_json='{
      "name": "'${realm}'",
      "protocol": "openid-connect",
      "attributes": {
        "include.in.token.scope": "true",
        "display.on.consent.screen": "true"
      },
      "protocolMappers": [
        {
          "name": "'${client}'-audience",
          "protocol": "openid-connect",
          "protocolMapper": "oidc-audience-mapper",
          "consentRequired": false,
          "config": {
            "included.client.audience": "'${client}'",
            "id.token.claim": "true",
            "access.token.claim": "true"
          }
        },
        {
          "name": "trusted_researcher",
          "protocol": "openid-connect",
          "protocolMapper": "oidc-usermodel-attribute-mapper",
          "consentRequired": false,
          "config": {
            "userinfo.token.claim": "true",
            "user.attribute": "trusted_researcher",
            "id.token.claim": "true",
            "access.token.claim": "true",
            "claim.name": "trusted_researcher",
            "jsonType.label": "boolean"
          }
        },
        {
          "name": "'${OPA_SITE_ADMIN_KEY}'",
          "protocol": "openid-connect",
          "protocolMapper": "oidc-usermodel-attribute-mapper",
          "consentRequired": false,
          "config": {
            "userinfo.token.claim": "true",
            "user.attribute": "'${OPA_SITE_ADMIN_KEY}'",
            "id.token.claim": "true",
            "access.token.claim": "true",
            "claim.name": "'${OPA_SITE_ADMIN_KEY}'",
            "jsonType.label": "boolean"
          }
        }
      ]
    }'

  new_scope=`curl --stderr - \
    -i -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    -X POST -H "Content-Type: application/json" -d "${scope_json}" \
    "${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${realm}/client-scopes" -k | grep "Location:" \
    | sed -E s/.*client-scopes.\([a-z0-9-]+\).*/\\\\1/`

  echo "Created client scope ${new_scope}" | tee -a $LOGFILE
  
  # Will add / to listen only if it is present

  local client_json='{
    "clientId": "'"${client}"'",
    "enabled": true,
    "protocol": "openid-connect",
    "implicitFlowEnabled": true,
    "standardFlowEnabled": true,
    "publicClient": false,
    "redirectUris": [
      "'${TYK_LOGIN_TARGET_URL}${redirect}'"
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
    },
    "defaultClientScopes": [
      "web-origins",
      "roles",
      "profile",
      "'${realm}'",
      "email"
    ]
  }'

  new_client=`curl --stderr - \
    -i -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    -X POST -H "Content-Type: application/json" -d "${client_json}" \
    "${KEYCLOAK_PUBLIC_URL}/auth/admin/realms/${realm}/clients" -k | grep "Location:" \
    | sed -E s/.*clients.\([a-z0-9-]+\).*/\\\\1/`
    # TODO: security issue fix this, -k flag above ignores cert, even if the url is https

  echo "Created client ${new_client}" | tee -a $LOGFILE
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

echo "    Starting setup calls to keycloak" | tee -a $LOGFILE

echo "Getting keycloak token" | tee -a $LOGFILE
KEYCLOAK_TOKEN=$(get_token)

echo "Creating Realm ${KEYCLOAK_REALM}" | tee -a $LOGFILE
set_realm ${KEYCLOAK_REALM}

echo "Setting client ${KEYCLOAK_CLIENT_ID} in base64" | tee -a $LOGFILE
export KEYCLOAK_CLIENT_ID_64=$(echo -n ${KEYCLOAK_CLIENT_ID} | base64)
echo $KEYCLOAK_CLIENT_ID_64 > tmp/secrets/keycloak-client-$KEYCLOAK_CLIENT_ID-id-64

echo "Remove ports on prod" | tee -a $LOGFILE
if [[ ${KEYCLOAK_PUBLIC_URL} == *":443"* ]]; then
  echo "option 1";
  export KEYCLOAK_PUBLIC_URL_PROD=$(echo ${KEYCLOAK_PUBLIC_URL} | sed -e 's/\(:443\)\$//g')
elif [[ ${KEYCLOAK_PUBLIC_URL} == *":80"* ]]; then
  echo "option 2";
  export KEYCLOAK_PUBLIC_URL_PROD=$(echo ${KEYCLOAK_PUBLIC_URL} | sed -e 's/\(:80\)\$//g')
else
  echo "option 3";
  export KEYCLOAK_PUBLIC_URL_PROD=$KEYCLOAK_PUBLIC_URL
fi ;

echo "Setting client ${KEYCLOAK_CLIENT_ID}" | tee -a $LOGFILE
set_client "${KEYCLOAK_REALM}" "${KEYCLOAK_CLIENT_ID}" "${KEYCLOAK_LOGIN_REDIRECT_PATH}"

echo "Getting keycloak secret" | tee -a $LOGFILE
KEYCLOAK_SECRET_RESPONSE=$(get_secret ${KEYCLOAK_REALM})
export KEYCLOAK_SECRET=$KEYCLOAK_SECRET_RESPONSE
echo $KEYCLOAK_SECRET > tmp/secrets/keycloak-client-$KEYCLOAK_CLIENT_ID-secret | tee -a $LOGFILE

echo "Getting keycloak public key" | tee -a $LOGFILE
KEYCLOAK_PUBLIC_KEY_RESPONSE=$(get_public_key ${KEYCLOAK_REALM})
export KEYCLOAK_PUBLIC_KEY=$KEYCLOAK_PUBLIC_KEY_RESPONSE
echo "Retrieved keycloak public key as ${KEYCLOAK_PUBLIC_KEY}" | tee -a $LOGFILE
echo $KEYCLOAK_PUBLIC_KEY > tmp/secrets/keycloak-public-key | tee -a $LOGFILE

if [[ ${KEYCLOAK_GENERATE_TEST_USER} == 1 ]]; then
  echo "Adding test user" | tee -a $LOGFILE
  add_user "$(cat tmp/secrets/keycloak-test-user)" "$(cat tmp/secrets/keycloak-test-user-password)" "trusted_researcher"
  add_user "$(cat tmp/secrets/keycloak-test-user2)" "$(cat tmp/secrets/keycloak-test-user2-password)" "stranger"
fi

#set_trusted_researcher "$(cat tmp/secrets/keycloak-test-user)"

echo "Waiting for keycloak to restart" | tee -a $LOGFILE
while ! docker logs --tail 5 ${CANDIG_AUTH_DOMAIN} | grep "Admin console listening on http://127.0.0.1:9990"; do sleep 1; done
echo "Keycloak setup done!" | tee -a $LOGFILE
