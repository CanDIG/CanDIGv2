ARG BASE_IMAGE
FROM ${BASE_IMAGE}

LABEL Maintainer="CanDIG Project"
LABEL "candigv2"="tyk"

# TODO: this image uses temp dir inside the lib/tyk which deviates from convention of this repo
# See tyk_preflight.sh for the same.
COPY ./tmp/tyk.conf /opt/tyk-gateway/tyk.conf
COPY ./tmp/middleware/authMiddleware.js /opt/tyk-gateway/middleware/authMiddleware.js
COPY ./tmp/middleware/backendAuthMiddleware.js /opt/tyk-gateway/middleware/backendAuthMiddleware.js
COPY ./tmp/middleware/frontendAuthMiddleware.js /opt/tyk-gateway/middleware/frontendAuthMiddleware.js
COPY ./tmp/middleware/permissionsStoreMiddleware.js /opt/tyk-gateway/middleware/permissionsStoreMiddleware.js
COPY ./tmp/middleware/virtualLogin.js /opt/tyk-gateway/middleware/virtualLogin.js
COPY ./tmp/middleware/virtualLogout.js /opt/tyk-gateway/middleware/virtualLogout.js
COPY ./tmp/middleware/virtualToken.js /opt/tyk-gateway/middleware/virtualToken.js
COPY ./tmp/apps /opt/tyk-gateway/apps
COPY ./tmp/policies/policies.json /opt/tyk-gateway/policies/policies.json

## Extra APIs can be added here
#COPY ./tmp/apps/api_example.json /opt/tyk-gateway/apps/api_example.json
