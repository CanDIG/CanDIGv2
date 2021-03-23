#! /usr/bin/env bash
set -e

# This script will set up a full keycloak environment on your local CanDIGv2 cluster

usage () {
  echo "Make sure to set relevant environment variables!"
  echo "Current setup: "
  echo "KEYCLOAK_ADMIN_USER: ${KEYCLOAK_ADMIN_USER}"
  echo "KEYCLOAK_ADMIN_PW: ${KEYCLOAK_ADMIN_PW}"
  echo "KEYCLOAK_TEST_USER: ${KEYCLOAK_TEST_USER}"
  echo "KEYCLOAK_TEST_PW: ${KEYCLOAK_TEST_PW}"
  echo "KEYCLOAK_TEST_USER: ${KEYCLOAK_TEST_USER_TWO}"
  echo "KEYCLOAK_TEST_PW: ${KEYCLOAK_TEST_PW_TWO}"
  echo "KEYCLOAK_SERVICE_PUBLIC_URL: ${KEYCLOAK_SERVICE_PUBLIC_URL}"
  echo "KEYCLOAK_SERVICE_PUBLIC_PORT: ${KEYCLOAK_SERVICE_PUBLIC_PORT}"
  echo "CANDIG_AUTH_DOMAIN: ${CANDIG_AUTH_DOMAIN}"

  echo
}


# Load Keycloak template (.tpl) files, populate them 
# with project .env variables, and then spit 
# them out to ./lib/keycloak/tmp/*


# echo 
mkdir -p ${PWD}/lib/authentication/keycloak/tmp

# Copy files from template configs
echo "Copying application-users.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/application-users.properties ${PWD}/lib/authentication/keycloak/tmp/application-users.properties

echo "Copying logging.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/logging.properties ${PWD}/lib/authentication/keycloak/tmp/logging.properties

echo "Copying mgmt-users.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/mgmt-users.properties ${PWD}/lib/authentication/keycloak/tmp/mgmt-users.properties

echo "Copying standalone.xml .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/standalone.xml ${PWD}/lib/authentication/keycloak/tmp/standalone.xml

echo "Copying standalone-ha.xml .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/standalone-ha.xml ${PWD}/lib/authentication/keycloak/tmp/standalone-ha.xml



# Verify if keycloak container is running
KEYCLOAK_CONTAINERS=$(echo $(docker ps | grep keycloak | wc -l))
echo "Number of keycloak containers running: ${KEYCLOAK_CONTAINERS}"
if [[ $KEYCLOAK_CONTAINERS -eq 0 ]]; then
   echo "Booting keycloak container!"
   docker-compose -f ${PWD}/lib/compose/docker-compose.yml -f ${PWD}/lib/authentication/docker-compose.yml up -d keycloak
   sleep 5
   echo ">> .. waiting for keycloak to start..."
   while !  docker logs --tail 1000  ${CANDIG_AUTH_DOMAIN} | grep "Undertow HTTPS listener https listening on 0.0.0.0" ; do sleep 1 ; done
   echo ">> .. ready..."
fi


###############

add_users() {
  # CANDIG_AUTH_DOMAIN is the name of the keycloak server inside the compose network
  echo "Adding ${KEYCLOAK_TEST_USER}"
  docker exec ${CANDIG_AUTH_DOMAIN} /opt/jboss/keycloak/bin/add-user-keycloak.sh -u ${KEYCLOAK_TEST_USER} -p ${KEYCLOAK_TEST_PW} -r ${KEYCLOAK_REALM}

  echo "Adding ${KEYCLOAK_TEST_USER_TWO}"
  docker exec ${CANDIG_AUTH_DOMAIN} /opt/jboss/keycloak/bin/add-user-keycloak.sh -u ${KEYCLOAK_TEST_USER_TWO} -p ${KEYCLOAK_TEST_PW_TWO} -r ${KEYCLOAK_REALM}

  echo "Restarting the keycloak container"
  docker restart ${CANDIG_AUTH_DOMAIN}
}

###############

get_token () {
  BID=$(curl \
    -d "client_id=admin-cli" \
    -d "username=$KEYCLOAK_ADMIN_USER" \
    -d "password=$KEYCLOAK_ADMIN_PW" \
    -d "grant_type=password" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/realms/master/protocol/openid-connect/token" -k 2> /dev/null )
  echo ${BID} | python3 -c 'import json,sys;obj=json.load(sys.stdin);print(obj["access_token"])'
}

###############

set_realm () {
  realm=$1

  JSON='{
    "realm": "candig",
    "enabled": true
  }'

  curl \
    -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    -X POST -H "Content-Type: application/json"  -d "${JSON}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms" -k
}


get_realm () {
  realm=$1

  curl \
    -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${realm}" -k | jq .
}

#################################

get_realm_clients () {
  realm=$1

  curl \
    -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${realm}/clients" -k | jq -S .
}


#################################
set_client () {
  realm=$1
  client=$2
  listen=$3
  redirect=$4

  # Will add / to listen only if it is present

  JSON='{
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
    -X POST -H "Content-Type: application/json"  -d "${JSON}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${realm}/clients" -k
}

get_secret () {
  id=$(curl -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    ${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${KEYCLOAK_REALM}/clients -k 2> /dev/null \
    | python3 -c 'import json,sys;obj=json.load(sys.stdin); print([l["id"] for l in obj if l["clientId"] ==
    "'"$KEYCLOAK_CLIENT_ID"'" ][0])')

  curl -H "Authorization: bearer ${KEYCLOAK_TOKEN}" \
    ${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${KEYCLOAK_REALM}/clients/$id/client-secret -k 2> /dev/null |\
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["value"])'
}

get_public_key () {
  curl \
    ${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/realms/${KEYCLOAK_REALM} -k 2> /dev/null |\
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["public_key"])'
}
##################################

# SCRIPT START

echo "-- Starting setup calls to keycloak --"
echo "$KEYCLOAK_ADMIN_USER $KEYCLOAK_ADMIN_PW $KEYCLOAK_SERVICE_PUBLIC_URL"

echo ">> Getting KEYCLOAK_TOKEN .."
KEYCLOAK_TOKEN=$(get_token)
#echo ">> retrieved KEYCLOAK_TOKEN ${KEYCLOAK_TOKEN}"
echo ">> .. got it..."

echo ">> Creating Realm ${KEYCLOAK_REALM} .."
set_realm ${KEYCLOAK_REALM}
echo ">> .. created..."


echo ">> Setting client KEYCLOAK_CLIENT_ID .."
set_client ${KEYCLOAK_REALM} ${KEYCLOAK_CLIENT_ID} "${TYK_LISTEN_PATH}" ${KEYCLOAK_LOGIN_REDIRECT_PATH}
echo ">> .. set..."

echo ">> Getting KEYCLOAK_SECRET .."
export KEYCLOAK_SECRET=$(get_secret  ${KEYCLOAK_REALM})
echo "** Retrieved KEYCLOAK_SECRET as ${KEYCLOAK_SECRET} **"
echo ">> .. got it..."
echo


echo ">> Getting KEYCLOAK_PUBLIC_KEY .."
export KEYCLOAK_PUBLIC_KEY=$(get_public_key  ${KEYCLOAK_REALM})
echo "** Retrieved KEYCLOAK_PUBLIC_KEY as ${KEYCLOAK_PUBLIC_KEY} **"
echo ">> .. got it..."
echo


echo ">> Adding user .."
add_users
echo ">> .. added..."
echo 

echo ">> .. waiting for keycloak to restart..."
while !  docker logs --tail 5  ${CANDIG_AUTH_DOMAIN} | grep "Admin console listening on http://127.0.0.1:9990" ; do sleep 1 ; done
echo ">> .. ready..."
