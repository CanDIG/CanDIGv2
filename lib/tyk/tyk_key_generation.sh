#!/usr/bin/env bash

set -Eeuo pipefail


echo "Starting Tyk key setup, post launch"

TYK_KEY_REQUEST=$(cat "${CONFIG_DIR}/key_request.json")
curl "${TYK_LOGIN_TARGET_URL}/tyk/keys/create" -H "x-tyk-authorization: ${TYK_SECRET_KEY}" -s -H "Content-Type: application/json" -X POST -d "${TYK_KEY_REQUEST}"
curl -H "x-tyk-authorization: ${TYK_SECRET_KEY}" -s "${TYK_LOGIN_TARGET_URL}/tyk/reload/group"

echo "Finished Tyk key setup"