#!/usr/bin/env bash

# Early-abort if this step isn't required
if [[ ! -z ${LOCAL_IP_ADDR:-} ]]; then
    echo "IP Address is already set to: $LOCAL_IP_ADDR"
    return
fi

# Find local IP address:
if [ "$VENV_OS" == "linux" ]; then
    ip addr | grep -A 1 'wlp[0-9]\|eth[0-9]\|ens[0-9]' | grep -o "inet [0-9.]\+" | cut -d' ' -f2 > .hosts.tmp2
else
    ifconfig | awk '/inet /&&!/127.0.0.1/{print $2;exit}' > .hosts.tmp2
fi

numlines=$(cat .hosts.tmp2 | wc -l) # use cat to prevent the name of the file from being printed on some systems
if [ "$numlines" == "1" ]; then
    export LOCAL_IP_ADDR=`cat .hosts.tmp2`
elif [ "$numlines" == "0" ]; then
    echo "ERROR: Your internet adapter could not be found automatically. Please determine your local IP address,"
    echo "set LOCAL_IP_ADDR=<your local network IP address> (e.g. 192.168.x.x) in your .env file, then restart conda"
    cat .hosts.tmp2
else
    echo "ERROR: More than one IP has been detected. Since this script can't automatically determine which one"
    echo "will make the build work, please set LOCAL_IP_ADDR=<your local network IP address> (e.g. 192.168.x.x)"
    echo "in your .env file, then restart conda"
    cat .hosts.tmp2
fi
rm .hosts.tmp2;
