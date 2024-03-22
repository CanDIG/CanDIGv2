# This script creates and configures a client within a Keycloak realm

echo
echo -e "${BLUE}Creating client: $KEYCLOAK_CLIENT_ID${DEFAULT}"

CLIENT_OUTPUT=$(KCADM create clients -r "$KEYCLOAK_REALM" \
    -s clientId="$KEYCLOAK_CLIENT_ID" \
    -s enabled=true \
    -s protocol=openid-connect \
    -s publicClient=false \
    -s clientAuthenticatorType=client-secret \
    -s standardFlowEnabled=true \
    -s directAccessGrantsEnabled=true \
    -s 'redirectUris=["'"$TYK_LOGIN_TARGET_URL$KEYCLOAK_LOGIN_REDIRECT_PATH"'"]' \
    -s 'webOrigins=["'"$TYK_LOGIN_TARGET_URL"'"]' 2>&1)

echo $CLIENT_OUTPUT
# Extract the client ID from the output
CLIENT_ID=$(echo $CLIENT_OUTPUT | grep -oE '[0-9a-fA-F-]{36}')

# Create client scopes
SCOPE_NAME="${KEYCLOAK_CLIENT_ID}-audience"
KCADM create clients/$CLIENT_ID/protocol-mappers/models -r $KEYCLOAK_REALM \
    -s name=$SCOPE_NAME \
    -s protocol=openid-connect \
    -s protocolMapper=oidc-audience-mapper \
    -s config="{\"included.client.audience\" : \"$KEYCLOAK_CLIENT_ID\",\"id.token.claim\" : \"true\",\"access.token.claim\" : \"true\"}"

# EXPORT: Get the client secret and save it to secrets
CLIENT_SECRET=$(KCADM get clients/"$CLIENT_ID"/client-secret -r "$KEYCLOAK_REALM" | jq -r '.value')
echo "$CLIENT_SECRET" > tmp/secrets/keycloak-client-$KEYCLOAK_CLIENT_ID-secret

# EXPORT: Encode the Keycloak client ID in base64 and save it to secrets
KEYCLOAK_CLIENT_ID_64=$(echo -n "${KEYCLOAK_CLIENT_ID}" | base64)
echo "$KEYCLOAK_CLIENT_ID_64" > "tmp/secrets/keycloak-client-${KEYCLOAK_CLIENT_ID}-id-64"
