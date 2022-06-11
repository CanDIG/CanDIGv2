#!/usr/bin/env bash

set -Eeuo pipefail

LOGFILE=$PWD/tmp/progress.txt


echo "Starting Tyk key setup, post launch" | tee -a $LOGFILE

echo "Lets wait for Redis and Tyk to get up" | tee -a $LOGFILE
# if this fails in the future add a more robust test
sleep 5;

TYK_SECRET_KEY_VAL=$(cat $PWD/tmp/secrets/tyk-secret-key)
export TYK_SECRET_KEY=$TYK_SECRET_KEY_VAL

generate_key() {

  # Extra APIs can be added here in the `access_rights` section

  local tyk_key_request='{
      "allowance": 1000,
      "rate": 1000,
      "per": 1,
      "expires": -1,
      "quota_max": -1,
      "org_id": "",
      "quota_renews": 1449051461,
      "quota_remaining": -1,
      "quota_renewal_rate": 60,
      "access_rights": {
          "'"${TYK_CANDIG_API_ID}"'": {
              "api_id": "'"${TYK_CANDIG_API_ID}"'",
              "api_name": "'"${TYK_CANDIG_API_SLUG}"'",
              "Versions": ["Default"]
          },
          "'"${TYK_KATSU_API_ID}"'": {
              "api_id": "'"${TYK_KATSU_API_ID}"'",
              "api_name": "'"${TYK_KATSU_API_SLUG}"'",
              "Versions": ["Default"]
          },
          "'"${TYK_CANDIG_DATA_PORTAL_API_ID}"'": {
              "api_id": "'"${TYK_CANDIG_DATA_PORTAL_API_ID}"'",
              "api_name": "'"${TYK_CANDIG_DATA_PORTAL_API_SLUG}"'",
              "Versions": ["Default"]
          },
          "'"${TYK_GRAPHQL_API_ID}"'": {
              "api_id": "'"${TYK_GRAPHQL_API_ID}"'",
              "api_name": "'"${TYK_GRAPHQL_API_SLUG}"'",
              "Versions": ["Default"]
          },
          "'"${TYK_HTSGET_API_ID}"'": {
              "api_id": "'"${TYK_HTSGET_API_ID}"'",
              "api_name": "'"${TYK_HTSGET_API_SLUG}"'",
              "Versions": ["Default"]
          }
      }
  }'

  curl "${TYK_LOGIN_TARGET_URL}/tyk/keys/create" -H "x-tyk-authorization: ${TYK_SECRET_KEY}" -s -H "Content-Type: application/json" -X POST -d "${tyk_key_request}"

  curl -H "x-tyk-authorization: ${TYK_SECRET_KEY}" -s "${TYK_LOGIN_TARGET_URL}/tyk/reload/group"

}

generate_key

echo "Finished Tyk key setup" | tee -a $LOGFILE