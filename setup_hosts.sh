#!/usr/bin/env bash

# Early-abort if this step isn't required
if [[ ! -z "$LOCAL_IP_ADDR" ]]; then
    echo "IP Address is already set to: $LOCAL_IP_ADDR"
    return
fi
if [[ "$CANDIG_DOMAIN" != "docker.localhost" ]]; then
    echo "Hosts step not required when CANDIG_DOMAIN != docker.localhost"
    return
fi

# Replace docker.localhost entry in /etc/hosts
if [ "$VENV_OS" == "linux" ]; then
    ip addr | grep -A 1 'wlp0\|eth0\|ens3' | grep -o "inet [0-9.]\+" | cut -d' ' -f2 > .hosts.tmp2
else
    ip addr | grep -o "inet [0-9.]\+" | cut -d' ' -f2 > .hosts.tmp2
fi

numlines=$(cat .hosts.tmp2 | wc -l) # use cat to prevent the name of the file from being printed on some systems
if [ "$numlines" == "1" ]; then
    export LOCAL_IP_ADDR=`cat .hosts.tmp2`
elif [ "$numlines" == "0" ]; then
    echo "ERROR: Your internet adapter could not be found automatically. Please determine your local IP address,"
    echo "and add it to /etc/hosts for the 'docker.localhost' host."
else
    echo "ERROR: More than one IP has been detected. Since this script can't automatically determine which one"
    echo "will make the build work, please set LOCAL_IP_ADDR=<your local network IP address> (e.g. 192.168.x.x)"
    echo "in your .env file, then restart conda"
fi
rm .hosts.tmp2;
