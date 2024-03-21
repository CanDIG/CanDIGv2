# This script creates and configures users within a Keycloak realm

echo
echo -e "${BLUE}Creating users${DEFAULT}"

create_user_and_set_password() {
    local USERNAME=$1
    local PASSWORD=$2
    local EMAIL=$3
    local FIRST_NAME=$4
    local LAST_NAME=$5

    $KCADM create users -r "$KEYCLOAK_REALM" \
        -s username="$USERNAME" \
        -s enabled=true \
        -s email="$EMAIL" \
        -s firstName="$FIRST_NAME" \
        -s lastName="$LAST_NAME"
    $KCADM set-password -r "$KEYCLOAK_REALM" --username "$USERNAME" --new-password "$PASSWORD"
}

# params: username password email firstname lastname
create_user_and_set_password "$(cat tmp/secrets/keycloak-test-user)" "$(cat tmp/secrets/keycloak-test-user-password)" "user1@test.ca" "One" "User"
create_user_and_set_password "$(cat tmp/secrets/keycloak-test-user2)" "$(cat tmp/secrets/keycloak-test-user2-password)" "user2@test.ca" "Two" "User"
