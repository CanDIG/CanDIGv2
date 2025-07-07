# This script creates and configures users within a Keycloak realm
echo -e "${BLUE}Creating users${DEFAULT}"

create_user_and_set_password() {
    # Note: KCADM set-password fails if the username has uppercase characters
    local USERNAME=$1
    local PASSWORD=$2
    local EMAIL=$3
    local FIRST_NAME=$4
    local LAST_NAME=$5

    KCADM create users -r "$KEYCLOAK_REALM" \
        -s username="$USERNAME" \
        -s enabled=true \
        -s email="$EMAIL" \
        -s firstName="$FIRST_NAME" \
        -s lastName="$LAST_NAME"
    KCADM set-password -r "$KEYCLOAK_REALM" --username "$USERNAME" --new-password "$PASSWORD"
}

# params: username password email firstname lastname
create_user_and_set_password "$CANDIG_NOT_ADMIN_USER" "$(cat tmp/keycloak/test-user-password)" "$CANDIG_NOT_ADMIN_USER" "One" "User"
create_user_and_set_password "$CANDIG_NOT_ADMIN2_USER" "$(cat tmp/keycloak/test-user2-password)" "$CANDIG_NOT_ADMIN2_USER" "Two" "User"
create_user_and_set_password "$DEFAULT_SITE_ADMIN_USER" "$(cat tmp/keycloak/test-site-admin-password)" "$DEFAULT_SITE_ADMIN_USER" "Site" "Admin"
