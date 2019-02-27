#! /usr/bin/env bash

set -xe

mc config host add minio http://minio:9000 $(cat /run/secrets/access_key) $(cat /run/secrets/secret_key)
