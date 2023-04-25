#!/usr/bin/env bash

if command -v getent >/dev/null 2>&1; then
    CANDIG_HOST=`getent hosts candig-dev`
elif command -v dscacheutil >/dev/null 2>&1; then
    CANDIG_HOST=`dscacheutil -q host -a name candig-dev`
fi

if [ ! -z "$CANDIG_HOST" ]; then
    printf "Please disable the UHN VPN, as it causes errors with the build process"
    exit 1
fi

DIFF_OUT=$(diff -I 'VENV_OS=.*' -I 'LOCAL_IP_ADDR=.*' -bwB etc/env/example.env .env)
if [ "$DIFF_OUT" == "" ]; then
    echo "Your .env matches etc/env/example.env, continuing"
else
    echo "Your .env differs from etc/env/example.env:"
    echo "$DIFF_OUT"
    while true
    do
        read -r -p 'Do you want to continue? ' choice
        case "$choice" in
          n|N) exit 1;;
          y|Y) exit 0;;
          *) echo 'Response not valid';;
        esac
    done
fi
