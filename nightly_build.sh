#!/bin/bash

PostToSlack () {
    echo -X POST -H 'Content-type: application/json' --data "{\"text\":\"$1\"}" https://hooks.slack.com/services/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
}

# Clean all
make clean-all
docker system prune -af

# Double check that the .env file works?
# But also we need to check that we can't just merge the .env file
git stash
git pull
git stash apply | tee stashapply.txt

if [ $? -ne 0]; then
    PostToSlack "Could not automatically merge .env: $(cat stashapply.txt)"
    return
fi

# How do we handle prod-specific changes?
make bin-conda

# Restart shell?
make init-conda
make build-all | tee lastbuild.txt

if [ $? -ne 0]; then
    PostToSlack "Build failed:\n $(cat lastbuild.txt)"
    return
fi

# Check the post-build check -- is everything ok?
make test-integration | tee integration-build.txt
if [ $? -ne 0]; then
    PostToSlack "Build failed:\n $(cat integration-build.txt)"
    return
fi

PostToSlack "Build success:\nhttp://candig-dev.hpc4healthlocal:5080/\nusername: user2\npassword $(cat tmp/secrets/keycloak-test-user2-password)"
