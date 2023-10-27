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

# copy entrypoint
COPY . /app

RUN touch initial_setup
# run vault
ENTRYPOINT ["bash", "/app/entrypoint.sh"]