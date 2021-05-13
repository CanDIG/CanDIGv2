ARG BASE_IMAGE
FROM ${BASE_IMAGE}

#TODO: add maintainer labels

#TODO: fix this image build
COPY ./tmp/authMiddleware.js /opt/tyk-gateway/middleware/authMiddleware.js
COPY ./tmp/permissionsStoreMiddleware.js /opt/tyk-gateway/middleware/permissionsStoreMiddleware.js
COPY ./tmp/tyk.conf /opt/tyk-gateway/tyk.conf
COPY ./tmp/virtualLogin.js /opt/tyk-gateway/middleware/virtualLogin.js
COPY ./tmp/virtualLogout.js /opt/tyk-gateway/middleware/virtualLogout.js
COPY ./tmp/virtualToken.js /opt/tyk-gateway/middleware/virtualToken.js
COPY ./tmp/api_candig.json /opt/tyk-gateway/apps/api_candig.json
COPY ./tmp/api_auth.json /opt/tyk-gateway/apps/api_auth.json
COPY ./tmp/policies.json /opt/tyk-gateway/policies/policies.json
