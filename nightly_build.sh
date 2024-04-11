#!/bin/bash

PostToSlack () {
    SAFE_TEXT=${1@Q}
    SAFE_TEXT=${SAFE_TEXT//\"/\\\"}
    curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$SAFE_TEXT\"}" $HOOK_URL
}


# Make sure all of our necessary configuration works
source nightly_env.sh
if [ -z "$HOOK_URL" ] || [ -z "$BOT_TOKEN" ]; then
    echo "Nightly build cannot work without the following settings set: \$HOOK_URL and \$BOT_TOKEN"
    exit
fi

# Clean all
make clean-all
docker system prune -af

# Double check that the .env file works?
# But also we need to check that we can't just merge the .env file
if [[ $SKIP_GIT -ne 1 ]]; then
    git stash push -m "NIGHTLY_STASH"
    git pull >tmp/gitpull.txt

    if [ $? -ne 0 ]; then
        PostToSlack "Could not automatically pull git repo: $(cat tmp/gitpull.txt)"
        exit
    fi

    git submodule update --recursive --init

    # Figure out the index of the stash we applied
    STASH_TEXT=$(git stash list | grep "NIGHTLY_STASH")
    if [[ ! -z $STASH_TEXT ]]; then
        [[ $STASH_TEXT =~ \{([[:digit:]]+)\} ]]
        git stash pop ${BASH_REMATCH[1]} 2<&1 >tmp/stashapply.txt
        if [ $? -ne 0 ]; then
            PostToSlack "Could not automatically merge git repo: $(cat tmp/stashapply.txt)"
            exit
        fi
    fi
fi

# Rerun nightly_env.sh in case anything changed in the .env file
source nightly_env.sh

# Re-initialize conda
make bin-conda
source bin/miniconda3/etc/profile.d/conda.sh
make init-conda
conda activate candig
make build-all ARGS="-s" 2<&1 >tmp/lastbuild.txt

if [ $? -ne 0 ]; then
    PostToSlack "Build failed:\n $(tail tmp/lastbuild.txt)"
    exit
fi

# Don't run integration tests until we see that every service has completed setup
TYK_TESTS=""
TRIES=0
while [ -z "$TYK_TESTS" ];
do
    TYK_TESTS=$(pytest -k "test_tyk" etc/tests/test_integration.py | grep "1 passed")
    sleep 15
    TRIES=$TRIES+1
    if [[ $TRIES -gt 120 ]]; then
        PostToSlack "Tyk did not go live after 30 minutes"
        exit
    fi
done

make test-integration 2<&1 >tmp/integration-build.txt
if [ $? -ne 0 ]; then
    PostToSlack "Integration tests failed:\n $(tail tmp/integration-build.txt)"
    exit
fi

# Run the ingestion
python settings.py
source env.sh
cd $INGEST_PATH
export CLINICAL_DATA_LOCATION=$INGEST_PATH/tests/clinical_ingest.json
# should be pip install -r requirements.txt, but that didn't seem to work last I checked -- dependency errors?
pip install -r requirements.txt
python katsu_ingest.py
cd $BUILD_PATH

PostToSlack "\`\`\`Build success:\nhttp://candig-dev.hpc4healthlocal:5080/\nusername: $(cat ./tmp/secrets/keycloak-test-site-admin)\npassword $(cat ./tmp/secrets/keycloak-test-site-admin-password)\`\`\`"

