# -*- mode: ruby -*-
# vi: set ft=ruby :

# Install vagrant-disksize to allow resizing the vagrant box disk.
unless Vagrant.has_plugin?("vagrant-disksize")
    raise  Vagrant::Errors::VagrantError.new, "vagrant-disksize plugin is missing. Please install it using 'vagrant plugin install vagrant-disksize' and rerun 'vagrant up'"
end

Vagrant.configure('2') do |config|
  config.vm.box = 'debian/contrib-buster64'
  config.vm.hostname = 'candig.local'
  # config.vm.network "forwarded_port", guest: 80, host: 80
  # config.vm.network "forwarded_port", guest: 443, host: 443
  config.vm.synced_folder '.', '/home/vagrant/candig', type: 'virtualbox'

  config.disksize.size = '50GB'
  config.vm.provider 'virtualbox' do |vb|
    vb.name = 'candig-dev'
    vb.gui = false
    vb.customize ['modifyvm', :id, '--cpus', 4]
    vb.customize ['modifyvm', :id, '--memory', '4096']
  end

  # run custom shell on provision
  config.vm.provision 'shell', privileged: false, path: "provision.sh", args: ["/home/vagrant/candig"]
end
