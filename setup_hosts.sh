#!/usr/bin/env bash

# Early-abort if this step isn't required
test=$(grep -E "\sdocker\.localhost" /etc/hosts)

if [[ ! -z "$test" ]]; then
    echo "Skipping hosts setup as docker.localhosts already exists there..."
    exit 0
fi

# Replace docker.localhost entry in /etc/hosts
echo "HACK ALERT"
echo "This step will introduce an entry into /etc/hosts so that requests to docker.localhost"
echo "will bounce off your local network. Root access will be required..."
cp /etc/hosts .hosts.tmp
printf "\n" >>.hosts.tmp

if [ "$VENV_OS" == "linux" ]; then
  ifconfig | grep -A 1 'wlp0\|eth0' | grep -o "inet [0-9.]\+" | cut -d' ' -f2 > .hosts.tmp2
else
  ifconfig | grep -o "inet [0-9.]\+" | cut -d' ' -f2 > .hosts.tmp2
fi

numlines=$(wc -l .hosts.tmp2)
if [ "$numlines" == "1" ]; then
    printf "$IP\tdocker.localhost" >> .hosts.tmp
    sudo mv .hosts.tmp /etc/hosts;
    rm .hosts.tmp2;
else
    echo "ERROR: More than one IP has been detected. Since this script can't automatically determine which one"
    echo "will make the build work, please remove all but one of the inserted docker.localhost lines in /etc/hosts."
    awk '{printf "%s\tdocker.localhost\n", $0}' .hosts.tmp2 >> .hosts.tmp
    sudo mv .hosts.tmp /etc/hosts;
    rm .hosts.tmp2;
fi
