#!/usr/bin/env bash

# run a command and check to see if the error message is the expected (innocuous) error. Only print output if it's not the expected error.
cmd=$1
expected=$2
echo $cmd | bash &> .tmp_store

grep -q "$expected" .tmp_store

if [[ $? -ne 0 ]]; then
    cat .tmp_store
    exit 1
fi
rm .tmp_store
