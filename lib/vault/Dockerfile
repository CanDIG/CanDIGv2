# From https://www.bogotobogo.com/DevOps/Docker/Docker-Vault-Consul.php
# base image
FROM alpine:3.7

# set vault version
ENV VAULT_VERSION 1.5.0

# maintainer
LABEL maintainer="brennan.brouillette@c3g.ca"

# create a new directory
RUN mkdir /vault
RUN mkdir /vault/config
WORKDIR /vault

# download dependencies
RUN apk --no-cache add \
      bash \
      ca-certificates \
      wget

# download and set up vault
RUN wget --quiet --output-document=/tmp/vault.zip https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip && \
    unzip /tmp/vault.zip -d /vault && \
    rm -f /tmp/vault.zip && \
    chmod +x .

# update PATH
ENV PATH="PATH=$PATH:$PWD"

# add the config file
COPY ./config/vault-config.json /vault/config/vault-config.json

# expose port 8200
EXPOSE 8200

# debugging
# RUN touch /tmp/run.sh
# RUN chmod +x /tmp/run.sh
# RUN echo "#!/bin/bash" >> /tmp/run.sh
# RUN echo "while true; do echo \"looping..\"; sleep 2; done" >> /tmp/run.sh
# ENTRYPOINT ["/tmp/run.sh"]

# run vault
ENTRYPOINT ["vault"]