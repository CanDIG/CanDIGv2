# This script creates and configures a client within a Keycloak realm
echo -e "${BLUE}Creating client: $KEYCLOAK_CLIENT_ID${DEFAULT}"

CREATE_OUTPUT=$(KCADM -full create clients -r "$KEYCLOAK_REALM" \
    -s clientId="$KEYCLOAK_CLIENT_ID" \
    -s enabled=true \
    -s protocol=openid-connect \
    -s publicClient=false \
    -s clientAuthenticatorType=client-secret \
    -s standardFlowEnabled=true \
    -s directAccessGrantsEnabled=true \
    -s 'redirectUris=["'"$TYK_LOGIN_TARGET_URL$KEYCLOAK_LOGIN_REDIRECT_PATH"'"]' \
    -s 'webOrigins=["'"$TYK_LOGIN_TARGET_URL"'"]' 2>&1)

# Extract the client ID from the output
CLIENT_ID=$(echo $CREATE_OUTPUT | grep -oE '[0-9a-fA-F-]{36}')

# Create client scopes
SCOPE_NAME="${KEYCLOAK_CLIENT_ID}-audience"
KCADM create clients/$CLIENT_ID/protocol-mappers/models -r $KEYCLOAK_REALM \
    -s name=$SCOPE_NAME \
    -s protocol=openid-connect \
    -s protocolMapper=oidc-audience-mapper \
    -s config="{\"included.client.audience\" : \"$KEYCLOAK_CLIENT_ID\",\"id.token.claim\" : \"true\",\"access.token.claim\" : \"true\"}"


# EXPORT client secret
CLIENT_SECRET=$(KCADM -full get clients/"$CLIENT_ID"/client-secret -r "$KEYCLOAK_REALM" | sed -n '/{/,/}/p' | jq -r '.value')
echo "$CLIENT_SECRET" > tmp/keycloak/client-secret
