# This script creates and configures a client within a Keycloak realm
echo -e "${BLUE}Creating client: $KEYCLOAK_CLIENT_ID${DEFAULT}"

ENABLE_ROPC="false"
if [ "${OIDC_CHAIN,,}" = "client" ] || [ "${OIDC_CHAIN,,}" = "ropc" ]; then
    ENABLE_ROPC="true"
fi

add_audience_scope() {
    local CLIENT_UUID="${1}"
    local AUDIENCE="${2}"
    local SCOPE_NAME="${CLIENT}-${AUDIENCE}-audience"
    KCADM create clients/$CLIENT_UUID/protocol-mappers/models -r $KEYCLOAK_REALM \
        -s name=$SCOPE_NAME \
        -s protocol=openid-connect \
        -s protocolMapper=oidc-audience-mapper \
        -s config="{\"included.client.audience\" : \"$AUDIENCE\",\"id.token.claim\" : \"true\",\"access.token.claim\" : \"true\"}"
}

CREATE_OUTPUT=$(KCADM -full create clients -r "$KEYCLOAK_REALM" \
    -s clientId="$KEYCLOAK_CLIENT_ID" \
    -s enabled=true \
    -s protocol=openid-connect \
    -s publicClient=false \
    -s clientAuthenticatorType=client-secret \
    -s standardFlowEnabled=true \
    -s directAccessGrantsEnabled=$ENABLE_ROPC \
    -s 'redirectUris=["'"$TYK_LOGIN_TARGET_URL$KEYCLOAK_LOGIN_REDIRECT_PATH"'","'"$AUTH_ACCEPT_URL"'"]' \
    -s 'webOrigins=["'"$TYK_LOGIN_TARGET_URL"'"]' 2>&1)

# Extract the client ID from the output
CLIENT_UUID=$(echo $CREATE_OUTPUT | grep -oE '[0-9a-fA-F-]{36}')

# Create client scopes
add_audience_scope "${CLIENT_UUID}" "${KEYCLOAK_CLIENT_ID}"

# EXPORT client secret
CLIENT_SECRET=$(KCADM -full get clients/"$CLIENT_UUID"/client-secret -r "$KEYCLOAK_REALM" | sed -n '/{/,/}/p' | jq -r '.value')
echo -n "$CLIENT_SECRET" > tmp/keycloak/client-secret

# If we're using client authorization, we'll also need a client for the admin
if [ "${OIDC_CHAIN,,}" = "client" ]; then
    # Note: The terminology here is confusing, because we use the word "ID" for a couple different things
    CREATE_OUTPUT=$(KCADM -full create clients -r "$KEYCLOAK_REALM" \
        -s clientId="$KEYCLOAK_SERVICE_CLIENT_ID" \
        -s enabled=true \
        -s protocol=openid-connect \
        -s publicClient=false \
        -s clientAuthenticatorType=client-secret \
        -s standardFlowEnabled=false \
        -s directAccessGrantsEnabled=false  2>&1)
    SERVICE_CLIENT_UUID=$(echo $CREATE_OUTPUT | grep -oE '[0-9a-fA-F-]{36}')

    # Service accounts need two audiences: one for themselves, and one for our usual CanDIG client
    # (without it they won't authenticate properly with Tyk)
    add_audience_scope "${SERVICE_CLIENT_UUID}" "${KEYCLOAK_CLIENT_ID}"
    add_audience_scope "${SERVICE_CLIENT_UUID}" "${KEYCLOAK_SERVICE_CLIENT_ID}"
fi

