#!/usr/bin/env bash

# works for a Debian-based box: 

sudo apt-get update
sudo apt-get install -y unzip bsdtar

# Ubuntu 18.04 by default installs virtualbox-5.2
sudo apt-get install -y virtualbox
# if that doesn't work, try the following:
# sudo add-apt-repository "deb [arch=amd64] https://download.virtualbox.org/virtualbox/debian buster contrib"
# wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
# sudo apt-get update
# sudo apt-get install virtualbox-5.2

wget -c https://releases.hashicorp.com/vagrant/2.0.3/vagrant_2.0.3_x86_64.deb
sudo dpkg -i vagrant_2.0.3_x86_64.deb
rm vagrant_2.0.3_x86_64.deb
vagrant plugin install vagrant-disksize
vagrant plugin install vagrant-openstack-provider
vagrant plugin install vagrant-reload
