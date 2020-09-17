#! /usr/bin/env bash

# Simple usage;
# Run prior to any code blocks that require sudo to avoid unexpected prompts
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi