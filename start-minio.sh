#!/usr/bin/env bash

set -xe

if [ ! -d "$(pwd)/etc/minio" ]; then
  mkdir -p $(pwd)/etc/minio/{config,data}
  #cp $(pwd)/lib/minio/sample.config.json $(pwd)/etc/minio/config/config.json
fi

if [ ! -f "$(pwd)/credentials" ]; then
  KEY=$(dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev)

  cat <<EOF > $(pwd)/credentials
admin
$KEY
EOF

else
  KEY=$(sed -n 2p credentials)
fi

docker run \
  -p 9000:9000 \
  --name minio1 \
  -e MINIO_ACCESS_KEY="admin" \
  -e MINIO_SECRET_KEY="$KEY" \
  -e MINIO_REGION="candig" \
  -e MINIO_DOMAIN="candig.com" \
  -v $(pwd)/etc/minio/data:/data \
  -v $(pwd)/etc/minio/config:/root/.minio \
  minio/minio server /data
