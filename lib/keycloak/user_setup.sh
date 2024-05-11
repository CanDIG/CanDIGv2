# This script creates and configures users within a Keycloak realm

echo
echo -e "${BLUE}Creating users${DEFAULT}"

create_user_and_set_password() {
    local USERNAME=$1
    local PASSWORD=$2
    local EMAIL=$3
    local FIRST_NAME=$4
    local LAST_NAME=$5

    CREATE_OUTPUT=$(KCADM create users -r "$KEYCLOAK_REALM" \
        -s username="$USERNAME" \
        -s enabled=true \
        -s email="$EMAIL" \
        -s firstName="$FIRST_NAME" \
        -s lastName="$LAST_NAME" 2>&1)
    # uncomment the line beblow to see the output
    # echo $CREATE_OUTPUT
    KCADM set-password -r "$KEYCLOAK_REALM" --username "$USERNAME" --new-password "$PASSWORD"
}

# params: username password email firstname lastname
create_user_and_set_password "$TEST_USER_1" "$(cat tmp/secrets/keycloak-test-user-password)" "$TEST_USER_1" "One" "User"
create_user_and_set_password "$TEST_USER_2" "$(cat tmp/secrets/keycloak-test-user2-password)" "$TEST_USER_2" "Two" "User"
create_user_and_set_password "$DEFAULT_SITE_ADMIN_USER" "$(cat tmp/secrets/keycloak-test-site-admin-password)" "$DEFAULT_SITE_ADMIN_USER" "Site" "Admin"
