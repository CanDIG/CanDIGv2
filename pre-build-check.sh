#!/usr/bin/env bash

# Check 1: UHN VPN is up
if command -v getent >/dev/null 2>&1; then
    CANDIG_HOST=`getent hosts candig-dev`
elif command -v dscacheutil >/dev/null 2>&1; then
    CANDIG_HOST=`dscacheutil -q host -a name candig-dev`
fi

if [ ! -z "$CANDIG_HOST" ]; then
    printf "Please disable the UHN VPN, as it causes errors with the build process"
    exit 1
fi

# Check 2: The value of CANDIG_DOMAIN can be reached
if [ -z "$CANDIG_DOMAIN" ]; then
    echo "Note: \$CANDIG_DOMAIN is not set, possibly because this script was run directly from the command line."
else
    if command -v getent >/dev/null 2>&1; then
        TEST_DOMAIN=`getent hosts $CANDIG_DOMAIN`
    elif command -v dscacheutil >/dev/null 2>&1; then
        TEST_DOMAIN=`dscacheutil -q host -a name $CANDIG_DOMAIN`
    fi

    if [ -z "$TEST_DOMAIN" ]; then
        echo "Please ensure the value of \$CANDIG_DOMAIN in your .env file points to this machine"
        echo "This should either be: 1) your local IP address, as assigned by your local network, or"
        echo "2) a domain name that resolves to this IP address"
        exit 1
    fi
fi

# Check 3: Submodules have been checked out
TEST_SUBMODULES=`ls -l lib/opa/opa | wc -l`

if [ "$TEST_SUBMODULES" -lt "2" ]; then
    echo "lib/opa/opa was not found"
    echo "Please ensure your submodules are checked out."
    echo "The command to do so is git submodule update --init --recursive"
    exit 1
fi

# Check 4: .env matches
DIFF_OUT=$(diff -I 'VENV_OS=.*' -I 'LOCAL_IP_ADDR=.*' -bwB etc/env/example.env .env)
if [ "$DIFF_OUT" == "" ]; then
    echo "Your .env matches etc/env/example.env, continuing"
else
    echo "Your .env differs from etc/env/example.env:"
    echo "$DIFF_OUT"
    while true
    do
        read -r -p 'Do you want to continue? (y/n)' choice
        case "$choice" in
          n|N) exit 1;;
          y|Y) exit 0;;
          *) echo 'Response not valid';;
        esac
    done
fi
