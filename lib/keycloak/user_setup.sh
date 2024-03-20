# This script creates and configures users within a Keycloak realm:
# 1. Checks if a user exists. If not, it creates a new user.
# 2. Updates the user configurations.

echo
echo -e "${BLUE}Creating users${DEFAULT}"

getUser() {
    local REALM_NAME=$1
    local USERNAME=$2

    local USER_ID=$($KCADM get users -r "$REALM_NAME" -q username="$USERNAME" | jq -r --arg USERNAME "$USERNAME" '.[] | select(.username==$USERNAME) | .id')
    echo "$USER_ID"
}

createUser() {
    local REALM_NAME=$1
    local USER_NAME=$2

    local USER_ID=$(getUser "$REALM_NAME" "$USER_NAME")
    if [[ -z "$USER_ID" ]]; then
        $KCADM create users -r "$REALM_NAME" -s username="$USER_NAME" -s enabled=true
        USER_ID=$(getUser "$REALM_NAME" "$USER_NAME") # Fetch again to get the ID
    else
        echo "User $USER_NAME already exists." >&2
    fi
    echo "$USER_ID"
}

initUser() {
    local USER_NAME=$1
    local PASSWORD=$2
    local EMAIL=$3
    local FIRST_NAME=$4
    local LAST_NAME=$5

    local USER_ID=$(createUser "$KEYCLOAK_REALM" "$USER_NAME")
    if [[ -n "$USER_ID" ]]; then
        $KCADM update users/$USER_ID -r "$KEYCLOAK_REALM" -s firstName="$FIRST_NAME" -s lastName="$LAST_NAME" -s email="$EMAIL"
        $KCADM set-password -r "$KEYCLOAK_REALM" --username "$USER_NAME" --new-password "$PASSWORD"
    fi
}

# params: username password email firstname lastname
initUser "$(cat tmp/secrets/keycloak-test-user)" "$(cat tmp/secrets/keycloak-test-user-password)" "user1@test.ca" "One" "User"
initUser "$(cat tmp/secrets/keycloak-test-user2)" "$(cat tmp/secrets/keycloak-test-user2-password)" "user2@test.ca" "Two" "User"
