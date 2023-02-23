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
echo "will bounce off your local network. Root access will be required, and this script assumes"
echo "that your ethernet adapter is named either wlp0 (wireless), eth0 (ethernet), or ens3 (debian)..."
cp /etc/hosts .hosts.tmp
printf "\n" >>.hosts.tmp

if [ "$VENV_OS" == "linux" ]; then
  ip addr | grep -A 1 'wlp0\|eth0\|ens3' | grep -o "inet [0-9.]\+" | cut -d' ' -f2 > .hosts.tmp2
else
  ip addr | grep -o "inet [0-9.]\+" | cut -d' ' -f2 > .hosts.tmp2
fi

numlines=$(cat .hosts.tmp2 | wc -l) # use cat to prevent the name of the file from being printed on some systems
if [ "$numlines" == "1" ]; then
    sudo cat .hosts.tmp2  | tr -d '\n' >> /etc/hosts
    sudo printf "\tdocker.localhost" >> /etc/hosts
    rm .hosts.tmp2
elif [ "$numlines" == "0" ]; then
    echo "ERROR: Your internet adapter could not be found automatically. Please determine your local IP address,"
    echo "and add it to /etc/hosts for the 'docker.localhost' host."
    exit 1
else
    echo "ERROR: More than one IP has been detected. Since this script can't automatically determine which one"
    echo "will make the build work, please remove all but one of the inserted docker.localhost lines in /etc/hosts."
    awk '{printf "%s\tdocker.localhost\n", $0}' .hosts.tmp2 >> .hosts.tmp
    sudo mv .hosts.tmp /etc/hosts;
    rm .hosts.tmp2;
    exit 1
fi
