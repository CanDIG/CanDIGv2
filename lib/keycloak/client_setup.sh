# This script creates and configures a client within a Keycloak realm

echo
echo -e "${BLUE}Creating client: $KEYCLOAK_CLIENT_ID${DEFAULT}"

CREATE_OUTPUT=$(KCADM create clients -r "$KEYCLOAK_REALM" \
    -s clientId="$KEYCLOAK_CLIENT_ID" \
    -s enabled=true \
    -s protocol=openid-connect \
    -s publicClient=false \
    -s clientAuthenticatorType=client-secret \
    -s standardFlowEnabled=true \
    -s directAccessGrantsEnabled=true \
    -s 'redirectUris=["'"$TYK_LOGIN_TARGET_URL$KEYCLOAK_LOGIN_REDIRECT_PATH"'"]' \
    -s 'webOrigins=["'"$TYK_LOGIN_TARGET_URL"'"]' 2>&1)
# uncomment the line beblow to see the output
# echo $CREATE_OUTPUT

# Extract the client ID from the output
CLIENT_ID=$(echo $CREATE_OUTPUT | grep -oE '[0-9a-fA-F-]{36}')

# Create client scopes
SCOPE_NAME="${KEYCLOAK_CLIENT_ID}-audience"
CREATE_OUTPUT=$(KCADM create clients/$CLIENT_ID/protocol-mappers/models -r $KEYCLOAK_REALM \
    -s name=$SCOPE_NAME \
    -s protocol=openid-connect \
    -s protocolMapper=oidc-audience-mapper \
    -s config="{\"included.client.audience\" : \"$KEYCLOAK_CLIENT_ID\",\"id.token.claim\" : \"true\",\"access.token.claim\" : \"true\"}" 2>&1)
# uncomment the line below to see the output
# echo $CREATE_OUTPUT

# EXPORT: Get the client secret and save it to secrets
# echo $CLIENT_ID
# echo $(KCADM get clients/"$CLIENT_ID"/client-secret -r "$KEYCLOAK_REALM")
CLIENT_SECRET=$(docker exec "$KEYCLOAK_CONTAINER_ID" /opt/keycloak/bin/kcadm.sh get clients/"$CLIENT_ID"/client-secret -r "$KEYCLOAK_REALM" | sed -n '/{/,/}/p' | jq -r '.value')
# echo $CLIENT_SECRET
echo "$CLIENT_SECRET" > tmp/secrets/keycloak-client-$KEYCLOAK_CLIENT_ID-secret
