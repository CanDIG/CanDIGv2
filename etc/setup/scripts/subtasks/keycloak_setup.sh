#! /usr/bin/env bash
# This script will set up a full keycloak environment on your local CanDIGv2 cluster

usage () {
  echo "Make sure to set relevant environment variables!"
  echo "Current setup: "
  echo "KC_ADMIN_USER: ${KC_ADMIN_USER}"
  echo "KC_ADMIN_PW: ${KC_ADMIN_PW}"
  echo "KC_TEST_USER: ${KC_TEST_USER}"
  echo "KC_TEST_PW: ${KC_TEST_PW}"
  echo "KEYCLOAK_SERVICE_PUBLIC_URL: ${KEYCLOAK_SERVICE_PUBLIC_URL}"
  echo "KEYCLOAK_SERVICE_PUBLIC_PORT: ${KEYCLOAK_SERVICE_PUBLIC_PORT}"
  echo "CONTAINER_NAME_CANDIG_AUTH: ${CONTAINER_NAME_CANDIG_AUTH}"

  echo
}

# # Verify environment variables
# if [[ $KC_ADMIN_USER -eq "" ]] || [[ $KC_ADMIN_PW -eq "" ]] || [[ $KC_TEST_USER -eq "" ]] || [[ $KC_TEST_PW -eq "" ]]; then
#    usage
#    exit 1
# # elif [[ $# -eq 2 ]]; then
# #   KEYCLOAK_SERVICE_PUBLIC_URL=$1
# #   KEYCLOAK_SERVICE_PUBLIC_PORT=$2
# # elif [[ $# -gt 2 ]]; then
# #   usage
# #   exit 1
# fi

# Load Keycloak template (.tpl) files, populate them 
# with project .env variables, and then spit 
# them out to ./lib/keyclaok/volumes/*

# secrets.env
echo "Working on secrets.env .."
envsubst < ${PWD}/etc/setup/templates/configs/keycloak/configuration/secrets.env.tpl > ${PWD}/lib/keycloak/volumes/secrets.env
#temp
#touch ${PWD}/lib/keycloak/volumes/secrets.env

# echo 
mkdir ${PWD}/lib/keycloak/volumes/keycloak-db
chmod 777 ${PWD}/lib/keycloak/volumes/keycloak-db


# Copy files from template configs
echo "Copying application-roles.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/application-roles.properties ${PWD}/lib/keycloak/volumes/application-roles.properties

echo "Copying application-users.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/application-users.properties ${PWD}/lib/keycloak/volumes/application-users.properties

echo "Copying logging.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/logging.properties ${PWD}/lib/keycloak/volumes/logging.properties

echo "Copying mgmt-groups.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/mgmt-groups.properties ${PWD}/lib/keycloak/volumes/mgmt-groups.properties

echo "Copying mgmt-users.properties .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/mgmt-users.properties ${PWD}/lib/keycloak/volumes/mgmt-users.properties

echo "Copying standalone.xml .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/standalone.xml ${PWD}/lib/keycloak/volumes/standalone.xml

echo "Copying standalone-ha.xml .."
cp ${PWD}/etc/setup/templates/configs/keycloak/configuration/standalone-ha.xml ${PWD}/lib/keycloak/volumes/standalone-ha.xml



# Verify if keycloak container is running
KEYCLOAK_CONTAINERS=$(echo $(docker ps | grep keycloak | wc -l))
echo "Number of keycloak containers running: ${KEYCLOAK_CONTAINERS}"
if [[ $KEYCLOAK_CONTAINERS -eq 0 ]]; then
   echo "Booting keycloak container!"
   docker-compose -f ${PWD}/lib/keycloak/docker-compose.yml up -d
   sleep 5
fi


###############

add_user() {
  # CONTAINER_NAME_CANDIG_AUTH is the name of the keycloak server inside the compose network
  docker exec ${CONTAINER_NAME_CANDIG_AUTH} /opt/jboss/keycloak/bin/add-user-keycloak.sh -u ${KC_TEST_USER} -p ${KC_TEST_PW} -r ${KC_REALM}
  echo "Restarting the keycloak container"
  docker restart ${CONTAINER_NAME_CANDIG_AUTH}
}

###############

get_token () {
  BID=$(curl \
    -d "client_id=admin-cli" \
    -d "username=$KC_ADMIN_USER" \
    -d "password=$KC_ADMIN_PW" \
    -d "grant_type=password" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/realms/master/protocol/openid-connect/token" 2> /dev/null )
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
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms"
}


get_realm () {
  realm=$1

  curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${realm}" | jq .
}

#################################

get_realm_clients () {
  realm=$1

  curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${realm}/clients" | jq -S .
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
    "${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${realm}/clients"
}

get_secret () {
  id=$(curl -H "Authorization: bearer ${KC_TOKEN}" \
    ${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${KC_REALM}/clients 2> /dev/null \
    | python3 -c 'import json,sys;obj=json.load(sys.stdin); print([l["id"] for l in obj if l["clientId"] ==
    "'"$KC_CLIENT_ID"'" ][0])')

  curl -H "Authorization: bearer ${KC_TOKEN}" \
    ${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/admin/realms/${KC_REALM}/clients/$id/client-secret 2> /dev/null |\
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["value"])'
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

echo ">> Adding user .."
add_user
echo ">> .. added..."

while !  docker logs --tail 5  ${CONTAINER_NAME_CANDIG_AUTH} | grep "Admin console listening on http://127.0.0.1:9990" ; do sleep 1 ; done
docker exec ${CONTAINER_NAME_CANDIG_AUTH}  rm /opt/jboss/keycloak/standalone/configuration/keycloak-add-user.json 2> /dev/null
