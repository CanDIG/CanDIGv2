ARG alpine_version
FROM alpine:${alpine_version}

LABEL Maintainer="CanDIG Project"
LABEL "candigv2"="vault"

USER root

RUN apk update

RUN apk add --no-cache \
	bash \
	expect \
	jq \
	curl

WORKDIR /app

# add the config file
COPY ./tmp/vault-config.json /vault/config/vault-config.json

# copy entrypoint
COPY . /vault
RUN mkdir /vault/data
RUN chmod 777 /vault/data

RUN touch initial_setup
# run vault
ENTRYPOINT ["bash", "/vault/entrypoint.sh"]