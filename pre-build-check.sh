#!/usr/bin/env bash

SILENT_MODE=0
if [[ $* == *-s* ]]; then
    SILENT_MODE=1
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
DIFF_OUT=$(diff -I 'VENV_OS=.*' -I 'LOCAL_IP_ADDR=.*' -I '.*KEEP_TEST_DATA=.*' -bwB etc/env/example.env .env)
if [ "$DIFF_OUT" == "" ]; then
    echo "Your .env matches etc/env/example.env, continuing"
else
    echo "Your .env differs from etc/env/example.env:"
    echo "$DIFF_OUT"
    while [[ "$SILENT_MODE" != 1 ]]
    do
        read -r -p 'Do you want to continue? (y/n)' choice
        case "$choice" in
          n|N) exit 1;;
          y|Y) break;;
          *) echo 'Response not valid';;
        esac
    done
fi

# Check 4: is envsubst installed?
envsubst --version
if [[ $? -ne 0 ]]; then
    echo "envsubst/gettext is not installed on your machine. Install gettext with your package manager of choice."
    exit 1
fi

# Check 5: is jq installed?
jq --version
if [[ $? -ne 0 ]]; then
    echo "jq is not installed on your machine. Follow instructions at https://jqlang.github.io/jq/download/"
    exit 1
fi

# Check 6: is yq installed?
YQ_VER=$(yq --version | sed 's/[^0-9 .]//g')  # e.g. " 4.40.5" or " 3.2.3"
if [[ $? -ne 0 ]]; then
    echo "yq is not installed on your machine. Follow instructions at https://github.com/mikefarah/yq/#install"
    exit 1
else
    # Check the major version
    YQ_TRUNC=${YQ_VER##* }    # Everything after the last space e.g. "4.40.5" or "3.2.3"
    YQ_MAJ=${YQ_TRUNC%%.*}    # Everything before the first period e.g. "4" or "3"
    if [[ "$YQ_MAJ" -lt "4" ]]; then
        echo "Either yq is not installed, or the installed version of yq on your machine is out of date ($YQ_VER). Please update to version 4 or later by following instructions at https://github.com/mikefarah/yq/#install"
        exit 1
    fi
fi

