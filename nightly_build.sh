#!/bin/bash

PostToSlack () {
    SAFE_TEXT=${1@Q}
    SAFE_TEXT=${SAFE_TEXT//\"/\\\"}
    curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$SAFE_TEXT\"}" $HOOK_URL
}


# Make sure all of our necessary configuration works
HOOK_URL=$(cat hook_url.txt)
BOT_TOKEN=$(cat bot_token.txt)
if [ -z "$HOOK_URL" ] || [ -z "$BOT_TOKEN" ]; then
    echo "Nightly build cannot work without the following settings set: \$HOOK_URL and \$BOT_TOKEN"
    exit
fi

# Clean all
make clean-all
docker system prune -af

# Double check that the .env file works?
# But also we need to check that we can't just merge the .env file
git stash
git pull
git submodule update --recursive --init
git stash apply 2<&1 >stashapply.txt

if [ $? -ne 0 ]; then
    PostToSlack "Could not automatically merge git repo: $(tail stashapply.txt)"
    exit
fi

# How do we handle prod-specific changes?
make bin-conda

# Restart shell?
make init-conda
source bin/miniconda3/etc/profile.d/conda.sh
conda activate candig
make build-all ARGS="-s" 2<&1 >lastbuild.txt

if [ $? -ne 0 ]; then
    PostToSlack "Build failed:\n $(tail lastbuild.txt)"
    exit
fi

# Don't run integration tests until we see that HTSGet has completed setup
HTSGET_TEST=""
while [ -z "$HTSGET_TEST" ];
do
    HTSGET_TEST=$(curl -s http://candig-dev.hpc4healthlocal:3333/ga4gh/drs/v1/service-info | grep "DRS")
    sleep 5
done

make test-integration 2<&1 >integration-build.txt
if [ $? -ne 0 ]; then
    PostToSlack "Integration tests failed:\n $(tail integration-build.txt)"
    exit
fi

# Run the ingestion
python settings.py
source env.sh
export INGEST_PATH=$(cat ingestion_path.txt)
cd $INGEST_PATH
export CLINICAL_DATA_LOCATION=$INGEST_PATH/tests/clinical_ingest.json
pip install dateparser
pip install openapi_spec_validator
python katsu_ingest.py

PostToSlack "Build success:\nhttp://candig-dev.hpc4healthlocal:5080/\nusername: user2\npassword $(cat ./tmp/secrets/keycloak-test-user2-password)\ntoken $TOKEN"

# # Listen for a token posted to Slack, posted at most 20 hours ago
# OTHER_TOKEN=""
# let "OLDEST_DATE=$(date +%s) - 20*60*60" # 20 hours ago in unix timestamp
# while [ -z "$OTHER_TOKEN" ];
# do
#     # Look for a thing that has a token
#     # NB: Parsing JSON in bash is painful, so I'm offloading this to a python script
#     OTHER_TOKEN=$(python nightly_build_token.py --token $BOT_TOKEN)
#     if [ $? -eq 0 ]; then
#         OTHER_TOKEN=""
#     fi
#     sleep 30
# done
# 
# python add-federated-server.py -token $OTHER_TOKEN -id token -url url -keycloak keycloak -name federation-2 -province Ontario -code ON
