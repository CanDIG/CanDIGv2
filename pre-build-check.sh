#!/usr/bin/env bash

CANDIG_HOST=`getent hosts candig-dev`
if [ ! -z "$CANDIG_HOST" ]; then
    printf "Please disable the UHN VPN, as it causes errors with the build process"
    exit 1
fi
