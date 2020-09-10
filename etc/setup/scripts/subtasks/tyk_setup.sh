#! /bin/bash
# This script will set up a full tyk environment on your local CanDIGv2 cluster

# ** Be sure to invoke this from the Makefile at the project's root directory [CanDigV2] **

# Load Tyk template (.tpl) files, populate them 
# with project .env variables, and then spit 
# them out to ./lib/tyk/volumes/*


# api_auth.json
echo "Working on api_auth.json .."
envsubst < ${PWD}/etc/setup/templates/configs/tyk/confs/api_auth.json.tpl > ${PWD}/lib/tyk/volumes/api_auth.json

# api_candig.json
echo "Working on api_candig.json .."
envsubst < ${PWD}/etc/setup/templates/configs/tyk/confs/api_candig.json.tpl > ${PWD}/lib/tyk/volumes/api_candig.json

# policies.json
echo "Working on policies.json .."
envsubst < ${PWD}/etc/setup/templates/configs/tyk/confs/policies.json.tpl > ${PWD}/lib/tyk/volumes/policies.json

# tyk.conf
echo "Working on tyk.conf .."
envsubst < ${PWD}/etc/setup/templates/configs/tyk/confs/tyk.conf.tpl > ${PWD}/lib/tyk/volumes/tyk.conf

## TODO: tyk_analytics.conf , key_request.json.tpl


# Copy files from template configs
echo "Copying authMiddleware.js .."
cp ${PWD}/etc/setup/templates/configs/tyk/confs/authMiddleware.js ${PWD}/lib/tyk/volumes/authMiddleware.js

echo "Copying oidcDistributedClaimsConduitMiddleware.js .."
cp ${PWD}/etc/setup/templates/configs/tyk/confs/oidcDistributedClaimsConduitMiddleware.js ${PWD}/lib/tyk/volumes/oidcDistributedClaimsConduitMiddleware.js

echo "Copying virtualLogin.js .."
cp ${PWD}/etc/setup/templates/configs/tyk/confs/virtualLogin.js ${PWD}/lib/tyk/volumes/virtualLogin.js

echo "Copying virtualLogout.js .."
cp ${PWD}/etc/setup/templates/configs/tyk/confs/virtualLogout.js ${PWD}/lib/tyk/volumes/virtualLogout.js

echo "Copying virtualToken.js .."
cp ${PWD}/etc/setup/templates/configs/tyk/confs/virtualToken.js ${PWD}/lib/tyk/volumes/virtualToken.js


echo "-- Tyk Setup Done! --"
echo
