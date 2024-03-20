# This script creates and configures a client within a Keycloak realm:
# 1. Checks if a client exists. If not, it creates a new client.
# 2. Updates the client configurations.

echo
echo -e "${BLUE}Creating client: $KEYCLOAK_CLIENT_ID${DEFAULT}"

getClient() {
    local REALM_NAME=$1
    local CLIENT_ID=$2

    local ID=$($KCADM get clients -r "$REALM_NAME" --fields id,clientId | jq -r --arg CLIENT_ID "$CLIENT_ID" '.[] | select(.clientId==$CLIENT_ID) | .id')
    echo "$ID"
}

createClient() {
    local REALM_NAME=$1
    local CLIENT_ID=$2
    
    local ID=$(getClient "$REALM_NAME" "$CLIENT_ID")
    if [[ -z "$ID" ]]; then
        $KCADM create clients -r "$REALM_NAME" -s clientId="$CLIENT_ID" -s enabled=true
        ID=$(getClient "$REALM_NAME" "$CLIENT_ID") # Re-fetch ID of the newly created client
    else
        echo "Client $CLIENT_ID already exists." >&2
    fi
    echo "$ID"
}

ID=$(createClient "$KEYCLOAK_REALM" "$KEYCLOAK_CLIENT_ID")
$KCADM update clients/"$ID" -r "$KEYCLOAK_REALM" \
  -s protocol=openid-connect \
  -s publicClient=false \
  -s clientAuthenticatorType=client-secret \
  -s standardFlowEnabled=true \
  -s directAccessGrantsEnabled=true \
  -s 'redirectUris=["'${TYK_LOGIN_TARGET_URL}${KEYCLOAK_LOGIN_REDIRECT_PATH}'"]' \
  -s 'webOrigins=["'${TYK_LOGIN_TARGET_URL}'"]'

# Create client scopes
$KCADM create clients/$ID/protocol-mappers/models -r $KEYCLOAK_REALM \
	-s name=${KEYCLOAK_CLIENT_ID}-audience \
    -s protocol=openid-connect \
	-s protocolMapper=oidc-audience-mapper \
    -s config="{\"included.client.audience\" : \"$KEYCLOAK_CLIENT_ID\",\"id.token.claim\" : \"true\",\"access.token.claim\" : \"true\"}"

# EXPORT: Get the client secret and save it to secrets
CLIENT_SECRET=$($KCADM get clients/"$ID"/client-secret -r "$KEYCLOAK_REALM" | jq -r '.value')
echo "$CLIENT_SECRET" > tmp/secrets/keycloak-client-$KEYCLOAK_CLIENT_ID-secret

# EXPORT: Encode the Keycloak client ID in base64 and save it to secrets
KEYCLOAK_CLIENT_ID_64=$(echo -n "${KEYCLOAK_CLIENT_ID}" | base64)
echo "$KEYCLOAK_CLIENT_ID_64" > "tmp/secrets/keycloak-client-${KEYCLOAK_CLIENT_ID}-id-64"
