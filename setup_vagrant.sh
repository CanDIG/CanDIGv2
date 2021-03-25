#!/usr/bin/env bash

# works for a Debian-based box

sudo apt-get update
sudo apt-get install -y virtualbox unzip bsdtar
wget -c https://releases.hashicorp.com/vagrant/2.0.3/vagrant_2.0.3_x86_64.deb
sudo dpkg -i vagrant_2.0.3_x86_64.deb
vagrant plugin install vagrant-disksize
