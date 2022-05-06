#!/usr/bin/env bash

set -Euo pipefail
rm /root/.minio/certs
mkdir /root/.minio/certs
cp /run/secrets/private.key /root/.minio/certs
cp /run/secrets/public.crt /root/.minio/certs

mkdir /root/.minio/certs/$CANDIG_DOMAIN
cp /run/secrets/private.key /root/.minio/certs/$CANDIG_DOMAIN/
cp /run/secrets/public.crt /root/.minio/certs/$CANDIG_DOMAIN/

top -b