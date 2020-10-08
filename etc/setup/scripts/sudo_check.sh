#! /usr/bin/env bash
set -e

# **
# At the time of writing, this is simply used for deleting many of 
# the files and directories that are generated and/or modified from processes internal
# to authZ containers themselves and are/become owned by root. To properly clean
# the remenants of an older execution, file deletion commands need to be run as sudo.
# Although, because checking for sudo from within the Makefile where this is taking place doesn't work,
# that responsibility is delegated to this tiny portable script. If it is not checked first, 
# errors tend to cascade and get very ugly.
# **

# Simple usage;
# Run prior to any code blocks that require sudo to avoid unexpected prompts
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi