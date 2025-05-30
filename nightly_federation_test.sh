#!/bin/bash

PostToSlack () {
    # Single quoting the string breaks formatting, so instead we rely on the \" -> \\" to make sure this doesn't break the curl
    # SAFE_TEXT=${1@Q}
    SAFE_TEXT=${1//\"/\\\"}
    echo $SAFE_TEXT
    curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$SAFE_TEXT\"}" $HOOK_URL
}

# Make sure all of our necessary configuration works
source nightly_env.sh
if [ -z "$HOOK_URL" ] || [ -z "$BOT_TOKEN" ]; then
    echo "Nightly build cannot work without the following settings set: \$HOOK_URL and \$BOT_TOKEN"
    exit
fi

# Attempt to run the nightly federation, depending on what we do
if [ $LOCAL_FEDERATION -eq 1 ]; then
    make test-local-federation
else
    make test-querying-federation ARGS="--color=no" >tmp/federation-test.txt 2<&1
    if [ $? -ne 0 ]; then
        PostToSlack "Federation tests:\n\`\`\`$(tail -c 300 tmp/federation-test.txt)\`\`\`"
    else
        PostToSlack "Federation tests succeeded"
    fi
fi
