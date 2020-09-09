#!/bin/bash

usage () {

  echo "${0} [-a]  [<keycloak host> <keycloak api port>]"
  echo "     -a    adds user  ${KC_TEST_USER} in realm ${KC_REALM}"
}
OPTIND=1
unset KC_ADD_USER
while getopts "a" opt; do
  case $opt in
    a)
      KC_ADD_USER=true
      ;;
   \?)
      usage
      exit 1
      ;;
  esac
done

shift $((OPTIND -1))
echo $#
echo $1
echo $2
if [[ $# -eq 1 ]]; then
   usage
   exit 1
elif [[ $# -eq 2 ]]; then
  KC_LOCAL_URL=$1
  KC_LOCAL_PORT=$2
elif [[ $# -gt 2 ]]; then
  usage
  exit 1
fi


# FUNCTIONS

valid_json () {

  putative=${1}

  echo $putative | python3 -c 'import json,sys;obj=json.load(sys.stdin)' 2> /dev/null
  ret_val=$?
  if [ $ret_val = 0 ]; then
     echo JSON is valid
  else
     echo JSON is not valid
     exit $ret_val
  fi

}

###############

add_user() {

# CONTAINER_NAME_CANDIG_AUTH is the name of the keycloak server inside the compose network
docker exec ${CONTAINER_NAME_CANDIG_AUTH} /opt/jboss/keycloak/bin/add-user-keycloak.sh -u ${KC_TEST_USER} -p ${KC_TEST_USER_PW} -r ${KC_REALM}
echo restarting Keycloak
docker restart ${CONTAINER_NAME_CANDIG_AUTH}
}

###############

get_token () {
  BID=$(curl \
    -d "client_id=admin-cli" \
    -d "username=$KC_ADMIN_USER" \
    -d "password=$KC_PW" \
    -d "grant_type=password" \
    "${KC_LOCAL_URL}:${KC_LOCAL_PORT}/auth/realms/master/protocol/openid-connect/token" 2> /dev/null )
  echo ${BID} | python3 -c 'import json,sys;obj=json.load(sys.stdin);print(obj["access_token"])'
}

######################

set_realm () {
  realm=$1

  JSON='{
  "realm": "'"${realm}"'",
  "enabled": true
}'


  curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    -X POST -H "Content-Type: application/json"  -d "${JSON}" \
    "${KC_LOCAL_URL}:${KC_LOCAL_PORT}/auth/admin/realms"

}

#######################

get_realm () {
  realm=$1
curl \
  -H "Authorization: bearer ${KC_TOKEN}" \
  "${KC_LOCAL_URL}:${KC_LOCAL_PORT}/auth/admin/realms/${realm}" | jq .
}


get_realm_clients () {
  realm=$1

curl \
  -H "Authorization: bearer ${KC_TOKEN}" \
  "${KC_LOCAL_URL}:${KC_LOCAL_PORT}/auth/admin/realms/${realm}/clients" | jq -S .
}


#################################
set_client () {
realm=$1
client=$2
listen=$3
redirect=$4

# Will add / to listen onlu if it is present


  JSON='{
  "clientId": "'"${client}"'",
  "enabled": true,
  "protocol": "openid-connect",
  "implicitFlowEnabled": true,
  "standardFlowEnabled": true,
  "publicClient": false,
  "redirectUris": [
   "'${CANDIG_PUBLIC_URL}${CD_PUB_PORT}${listen}${redirect}'"
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


  curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    -X POST -H "Content-Type: application/json"  -d "${JSON}" \
    "${KC_LOCAL_URL}:${KC_LOCAL_PORT}/auth/admin/realms/${realm}/clients"
}

get_secret () {

  id=$(curl -H "Authorization: bearer ${KC_TOKEN}" \
    ${KC_LOCAL_URL}:${KC_LOCAL_PORT}/auth/admin/realms/${KC_REALM}/clients 2> /dev/null \
    | python3 -c 'import json,sys;obj=json.load(sys.stdin); print([l["id"] for l in obj if l["clientId"] ==
    "'"$KC_CLIENT_ID"'" ][0])')

  curl -H "Authorization: bearer ${KC_TOKEN}" \
    ${KC_LOCAL_URL}:${KC_LOCAL_PORT}/auth/admin/realms/${KC_REALM}/clients/$id/client-secret 2> /dev/null |\
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["value"])'

}
##################################

# SCRIPT START

KC_TOKEN=$(get_token)

echo Create realm ${KC_REALM}
set_realm ${KC_REALM}


echo create_client ${KC_CLIENT_ID}
set_client ${KC_REALM} ${KC_CLIENT_ID} "${TYK_LISTEN_PATH}" ${KC_LOGIN_REDIRECT_PATH}

echo getting kc client secret
export KC_SECRET=$(get_secret  ${KC_REALM})

if $ADD_USER ; then
  add_user
fi
while !  docker logs --tail 5  ${CONTAINER_NAME_CANDIG_AUTH} | grep "Admin console listening on http://127.0.0.1:9990" ; do sleep 1 ; done
docker exec ${CONTAINER_NAME_CANDIG_AUTH}  rm /opt/jboss/keycloak/standalone/configuration/keycloak-add-user.json 2> /dev/null
