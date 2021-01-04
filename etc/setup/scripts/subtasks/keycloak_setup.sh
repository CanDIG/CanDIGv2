#! /usr/bin/env bash
set -e

# checks for dev or prod
if [ $MODE == "dev" ]
  then
    DEV_FLAG="-k"
fi
echo "--- MODE : ${MODE} ---"

# This script will set up a full keycloak environment on your local CanDIGv2 cluster

usage () {
  echo "Make sure to set relevant environment variables!"
  echo "Current setup: "
  echo "KC_ADMIN_USER: ${KC_ADMIN_USER}"
  echo "KC_ADMIN_PW: ${KC_ADMIN_PW}"
  echo "KC_TEST_USER: ${KC_TEST_USER}"
  echo "KC_TEST_PW: ${KC_TEST_PW}"
  echo "KC_TEST_USER: ${KC_TEST_USER_TWO}"
  echo "KC_TEST_PW: ${KC_TEST_PW_TWO}"
  echo "KEYCLOAK_SERVICE_PUBLIC_URL: ${KEYCLOAK_SERVICE_PUBLIC_URL}"
  echo "KEYCLOAK_SERVICE_PUBLIC_PORT: ${KEYCLOAK_SERVICE_PUBLIC_PORT}"
  echo "CANDIG_AUTH_CONTAINER_NAME: ${CANDIG_AUTH_CONTAINER_NAME}"

  echo
}


# Load Keycloak template (.tpl) files, populate them 
# with project .env variables, and then spit 
# them out to ./lib/keyclaok/data/*

mkdir -p ${PWD}/lib/authz/keycloak/data
sudo chown $USER ${PWD}/lib/authz/keycloak
sudo chown $USER ${PWD}/lib/authz/keycloak/data
sudo chgrp $USER ${PWD}/lib/authz/keycloak
sudo chown $USER ${PWD}/lib/authz/keycloak/data

# temp: in prod mode, explicitly indicating port 443 breaks vaults internal oidc provider checks.
# simply remove the ":443 from the authentication services public url for this purpose:
if [[ $KEYCLOAK_SERVICE_PUBLIC_URL == *":443"* ]]; then
    TEMP_KEYCLOAK_SERVICE_PUBLIC_URL=$(echo $KEYCLOAK_SERVICE_PUBLIC_URL | sed -e 's/\(:443\)$//g')
elif [[ $KEYCLOAK_SERVICE_PUBLIC_URL == *":80"* ]]; then
    TEMP_KEYCLOAK_SERVICE_PUBLIC_URL=$(echo $KEYCLOAK_SERVICE_PUBLIC_URL | sed -e 's/\(:80\)$//g')
else
    TEMP_KEYCLOAK_SERVICE_PUBLIC_URL=$(echo $KEYCLOAK_SERVICE_PUBLIC_URL)
fi

export TEMP_KEYCLOAK_SERVICE_PUBLIC_URL



# secrets.env
echo "Working on secrets.env .."
envsubst < ${PWD}/etc/setup/templates/configs/keycloak/configuration/secrets.env.tpl > ${PWD}/lib/authz/keycloak/data/secrets.env

# echo 
mkdir -p ${PWD}/lib/authz/keycloak/data/keycloak-db
chmod 777 ${PWD}/lib/authz/keycloak/data/keycloak-db


# Copy files from template configs
echo "Copying application-users.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/application-users.properties ${PWD}/lib/authz/keycloak/data/application-users.properties

echo "Copying logging.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/logging.properties ${PWD}/lib/authz/keycloak/data/logging.properties

echo "Copying mgmt-users.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/mgmt-users.properties ${PWD}/lib/authz/keycloak/data/mgmt-users.properties

echo "Copying standalone.xml .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/standalone.xml ${PWD}/lib/authz/keycloak/data/standalone.xml

echo "Copying standalone-ha.xml .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/standalone-ha.xml ${PWD}/lib/authz/keycloak/data/standalone-ha.xml



# Verify if keycloak container is running
KEYCLOAK_CONTAINERS=$(echo $(docker ps | grep keycloak | wc -l))
echo "Number of keycloak containers running: ${KEYCLOAK_CONTAINERS}"
if [[ $KEYCLOAK_CONTAINERS -eq 0 ]]; then
   echo "Booting keycloak container!"
   docker-compose -f ${PWD}/lib/authz/docker-compose.yml up -d keycloak
   sleep 5

   echo ">> .. waiting for keycloak to start..."
   while !  docker logs --tail 1000  ${CANDIG_AUTH_CONTAINER_NAME} | grep "Undertow HTTPS listener https listening on 0.0.0.0" ; do sleep 1 ; done
   echo ">> .. ready..."
fi


###############

add_users() {
  # CANDIG_AUTH_CONTAINER_NAME is the name of the keycloak server inside the compose network
  echo "Adding ${KC_TEST_USER}"
  docker exec ${CANDIG_AUTH_CONTAINER_NAME} /opt/jboss/keycloak/bin/add-user-keycloak.sh -u ${KC_TEST_USER} -p ${KC_TEST_PW} -r ${KC_REALM}

  echo "Adding ${KC_TEST_USER_TWO}"
  docker exec ${CANDIG_AUTH_CONTAINER_NAME} /opt/jboss/keycloak/bin/add-user-keycloak.sh -u ${KC_TEST_USER_TWO} -p ${KC_TEST_PW_TWO} -r ${KC_REALM}

  echo "Restarting the keycloak container"
  docker restart ${CANDIG_AUTH_CONTAINER_NAME}
}

###############

get_token () {
  BID=$(curl \
    -d "client_id=admin-cli" \
    -d "username=$KC_ADMIN_USER" \
    -d "password=$KC_ADMIN_PW" \
    -d "grant_type=password" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/realms/master/protocol/openid-connect/token" $DEV_FLAG 2> /dev/null )
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
    -H "Authorization: bearer ${KC_TOKEN}" \
    -X POST -H "Content-Type: application/json"  -d "${JSON}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms" $DEV_FLAG
}


get_realm () {
  realm=$1

  curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${realm}" $DEV_FLAG | jq .
}

#################################

get_realm_clients () {
  realm=$1

  curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${realm}/clients" $DEV_FLAG | jq -S .
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
    -H "Authorization: bearer ${KC_TOKEN}" \
    -X POST -H "Content-Type: application/json"  -d "${JSON}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${realm}/clients" $DEV_FLAG
}

get_secret () {
  id=$(curl -H "Authorization: bearer ${KC_TOKEN}" \
    ${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${KC_REALM}/clients $DEV_FLAG 2> /dev/null \
    | python3 -c 'import json,sys;obj=json.load(sys.stdin); print([l["id"] for l in obj if l["clientId"] ==
    "'"$KC_CLIENT_ID"'" ][0])')

  curl -H "Authorization: bearer ${KC_TOKEN}" \
    ${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${KC_REALM}/clients/$id/client-secret $DEV_FLAG 2> /dev/null |\
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["value"])'
}

get_public_key () {
  curl \
    ${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/realms/${KC_REALM} $DEV_FLAG 2> /dev/null |\
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["public_key"])'
}
##################################

# SCRIPT START

echo "-- Starting setup calls to keycloak --"
echo "$KC_ADMIN_USER $KC_ADMIN_PW $KEYCLOAK_SERVICE_PUBLIC_URL"

echo ">> Getting KC_TOKEN .."
KC_TOKEN=$(get_token)
#echo ">> retrieved KC_TOKEN ${KC_TOKEN}"
echo ">> .. got it..."

echo ">> Creating Realm ${KC_REALM} .."
set_realm ${KC_REALM}
echo ">> .. created..."


echo ">> Setting client KC_CLIENT_ID .."
set_client ${KC_REALM} ${KC_CLIENT_ID} "${TYK_LISTEN_PATH}" ${KC_LOGIN_REDIRECT_PATH}
echo ">> .. set..."

echo ">> Getting KC_SECRET .."
export KC_SECRET=$(get_secret  ${KC_REALM})
echo "** Retrieved KC_SECRET as ${KC_SECRET} **"
echo ">> .. got it..."
echo


echo ">> Getting KC_PUBLIC_KEY .."
export KC_PUBLIC_KEY=$(get_public_key  ${KC_REALM})
echo "** Retrieved KC_PUBLIC_KEY as ${KC_PUBLIC_KEY} **"
echo ">> .. got it..."
echo


echo ">> Adding user .."
add_users
echo ">> .. added..."
echo 

echo ">> .. waiting for keycloak to restart..."
while !  docker logs --tail 5  ${CANDIG_AUTH_CONTAINER_NAME} | grep "Admin console listening on http://127.0.0.1:9990" ; do sleep 1 ; done
echo ">> .. ready..."
