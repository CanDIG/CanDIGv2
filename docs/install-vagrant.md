# CanDIGv2 Install Guide

- - -

[Vagrant](https://www.vagrantup.com) can be used to automate the process of setting up a [Docker deployment](install-docker.md) of CanDIGv2 on a virtual machine on your local machine or to create an instance on an [OpenStack deployment](https://www.openstack.org).

## Set up Vagrant

You'll need to have compatible versions of [Vagrant](https://www.vagrantup.com) and [VirtualBox](https://www.virtualbox.org) on the system you'll be using to deploy the Vagrant VM. We tested using Vagrant 2.0.3 and VirtualBox 5.2: other versions may not play nicely together or load the plugins correctly.

If you're using a Debian or Ubuntu system, you can try running [setup_vagrant.sh](setup_vagrant.sh) to install the recommended versions. Otherwise, install the following:

* [Vagrant 2.0.3](https://releases.hashicorp.com/vagrant/2.0.3/) ([installation instructions](https://www.vagrantup.com/docs/installation))
* [VirtualBox 5.2.34](https://download.virtualbox.org/virtualbox/5.2.34/) ([installation instructions](https://www.virtualbox.org/manual/ch02.html))

Then install plugins:
```
vagrant plugin install vagrant-disksize
vagrant plugin install vagrant-openstack-provider
vagrant plugin install vagrant-reload
```
## Run Vagrant

By default, `vagrant up` will use the VirtualBox provider to create a VM on your local machine. 

You can also use Vagrant to deploy an instance on OpenStack:
* Get your credentials from your OpenStack dashboard: go to Project > API Access on the sidebar, then click the "Download OpenStack RC File" button and download the OpenStack RC File (Identity API v3).
* Either run the downloaded shell script to load the required environment variables, or export them into your shell directly.
* Export two additional environment variables:
  * `OS_KEYPAIR` should correspond to a valid keypair in OpenStack Dashboard > Project > Compute > Key Pairs. Choose one that does not have a passphrase associated with it.
  * `OS_PRIVATEKEY_PATH` should be the path of the private key associated with that keypair.
* Run `vagrant up --provider=openstack`.

After it's up, you can access your VM with `vagrant ssh`. If you want to suspend the VM, `vagrant suspend` or `vagrant halt` ([what's the difference?](https://stackoverflow.com/questions/42549087/in-vagrant-which-is-better-out-of-halt-and-suspend#42551494)). 

## Cleanup

To destroy your VM entirely, run `vagrant destroy`.

