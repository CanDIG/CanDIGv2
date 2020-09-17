#! /bin/bash
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi