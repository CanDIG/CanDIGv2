#!/bin/bash
#
# Nightly build: rebuild the CanDIG stack from develop branch
# Gitignored config (nightly_env.sh, .env, env.sh) and other untracked
# files are left untouched by the reset.

PostToSlack () {
    # Single quoting the string breaks formatting, so instead we rely on the \" -> \\" to make sure this doesn't break the curl
    # SAFE_TEXT=${1@Q}
    SAFE_TEXT=${1//\"/\\\"}
    echo $SAFE_TEXT
    curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$SAFE_TEXT\"}" $HOOK_URL
}

# Post a failure message to Slack and abort the run.
fail () {
    PostToSlack "$1"
    exit 1
}

# --- Preflight: make sure the configuration works ---------------------------
source nightly_env.sh
if [ -z "$HOOK_URL" ] || [ -z "$BOT_TOKEN" ]; then
    echo "Nightly build cannot work without the following settings set: \$HOOK_URL and \$BOT_TOKEN"
    exit 1
fi

BRANCH=${BRANCH:-develop}

# --- Clean all --------------------------------------------------------------
make clean-all
docker system prune -af

# --- Sync repo to a origin/$BRANCH ---------------------------------
if [[ $SKIP_GIT -ne 1 ]]; then
    git fetch origin >tmp/gitpull.txt 2>&1
    if [ $? -ne 0 ]; then
        fail "Could not fetch git repo:\n\`\`\`$(cat tmp/gitpull.txt)\`\`\`"
    fi

    # Hard-reset to the remote branch. Discards local tracked edits; leaves
    # gitignored config and untracked files in place.
    git checkout "$BRANCH" >>tmp/gitpull.txt 2>&1 \
        && git reset --hard "origin/$BRANCH" >>tmp/gitpull.txt 2>&1
    if [ $? -ne 0 ]; then
        fail "Could not reset to origin/$BRANCH:\n\`\`\`$(cat tmp/gitpull.txt)\`\`\`"
    fi

    git submodule sync --recursive >>tmp/gitpull.txt 2>&1
    git submodule update --init --recursive --force >>tmp/gitpull.txt 2>&1
    if [ $? -ne 0 ]; then
        fail "Could not update submodules:\n\`\`\`$(cat tmp/gitpull.txt)\`\`\`"
    fi
fi

# --- Build ------------------------------------------------------------------
# Re-source in case anything changed in the .env / nightly_env.sh files
source nightly_env.sh

# make bin-conda
# source bin/miniforge/etc/profile.d/conda.sh
# make init-conda
# conda activate candig
make build-all BUILD_OPTS="--no-cache" ARGS="-s" >tmp/lastbuild.txt 2>&1
if [ $? -ne 0 ]; then
    fail "Build failed:\n\`\`\`$(tail tmp/lastbuild.txt)\`\`\`"
fi

# --- Integration tests ------------------------------------------------------
# Don't run integration tests until we see that every service has completed setup
TYK_TESTS=""
TRIES=0
while [ -z "$TYK_TESTS" ];
do
    TYK_TESTS=$(make test-integration ARGS='-k "test_tyk" etc/tests/integration/test_integration.py' | grep "1 passed")
    sleep 15
    TRIES=$((TRIES+1))
    if [[ $TRIES -gt 120 ]]; then
        fail "Tyk did not go live after 30 minutes"
    fi
done

make test-integration ARGS="--color=no" >tmp/integration-build.txt 2>&1
if [ $? -ne 0 ]; then
    fail "Integration tests failed:\n\`\`\`$(tail tmp/integration-build.txt)\`\`\`"
fi

# --- Report success ---------------------------------------------------------
source env.sh

export TOKEN=$(python site_admin_token.py)

cd $BUILD_PATH

PostToSlack "\`\`\`\nBuild success:\n$TYK_LOGIN_TARGET_URL\nusername: $CANDIG_SITE_ADMIN_USER\npassword $CANDIG_SITE_ADMIN_PASSWORD\nusername: $CANDIG_NOT_ADMIN_USER\npassword $CANDIG_NOT_ADMIN_PASSWORD\nusername: $CANDIG_NOT_ADMIN2_USER\npassword $CANDIG_NOT_ADMIN2_PASSWORD\n\`\`\`"
FEDERATE_STRING="federate $TOKEN|$CANDIG_CLIENT_ID|$CANDIG_URL|$CANDIG_CLIENT_ID|ON|ca-on|$FEDERATION_SELF_SERVER_ID|$KEYCLOAK_PUBLIC_URL/auth/realms/$KEYCLOAK_REALM"
PostToSlack "\`\`\`$FEDERATE_STRING\`\`\`"
