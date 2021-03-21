ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY ./data/authMiddleware.js /opt/tyk-gateway/middleware/authMiddleware.js
COPY ./data/permissionsStoreMiddleware.js /opt/tyk-gateway/middleware/permissionsStoreMiddleware.js
COPY ./data/tyk.conf /opt/tyk-gateway/tyk.conf
COPY ./data/virtualLogin.js /opt/tyk-gateway/middleware/virtualLogin.js
COPY ./data/virtualLogout.js /opt/tyk-gateway/middleware/virtualLogout.js
COPY ./data/virtualToken.js /opt/tyk-gateway/middleware/virtualToken.js
COPY ./data/api_candig.json /opt/tyk-gateway/apps/api_candig.json
COPY ./data/api_auth.json /opt/tyk-gateway/apps/api_auth.json
COPY ./data/policies.json /opt/tyk-gateway/policies/policies.json
