#!/usr/bin/env bash

if command -v getent >/dev/null 2>&1; then
    CANDIG_HOST=`getent hosts candig-dev`
elif command -v dnscacheutil >/dev/null 2>&1; then
    CANDIG_HOST=`dscacheutil -q host -a name candig-dev`
fi

if [ ! -z "$CANDIG_HOST" ]; then
    printf "Please disable the UHN VPN, as it causes errors with the build process"
    exit 1
fi

