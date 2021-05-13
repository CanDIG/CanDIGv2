# -*- mode: ruby -*-
# vi: set ft=ruby :

# Install vagrant-disksize to allow resizing the vagrant box disk.
unless Vagrant.has_plugin?("vagrant-disksize")
    raise  Vagrant::Errors::VagrantError.new, "vagrant-disksize plugin is missing. Please install it using 'vagrant plugin install vagrant-disksize' and rerun 'vagrant up'"
end

# Install vagrant-reload to allow reloading during provisioning.
unless Vagrant.has_plugin?("vagrant-reload")
    raise  Vagrant::Errors::VagrantError.new, "vagrant-reload plugin is missing. Please install it using 'vagrant plugin install vagrant-reload' and rerun 'vagrant up'"
end

Vagrant.configure('2') do |config|
  config.vm.hostname = 'candig-dev'

  config.vm.provider 'virtualbox' do |vb, override|
    override.vm.synced_folder '.', '/home/vagrant/candig', type: 'virtualbox'
    override.vm.box = 'debian/contrib-buster64'
    override.vm.hostname = 'candig.local'
    override.disksize.size = '50GB'
#     override.vm.network "forwarded_port", guest: 80, host: 80
#     override.vm.network "forwarded_port", guest: 443, host: 443
    vb.name = 'candig-dev'
    vb.gui = false
    vb.customize ['modifyvm', :id, '--cpus', 4]
    vb.customize ['modifyvm', :id, '--memory', '4096']
    # run custom shell on provision
    override.vm.provision 'shell', privileged: false, path: "provision.sh", args: ["/home/vagrant/candig"]
    override.vm.provision :reload
    override.vm.provision 'shell', privileged: false, path: "setup_containers.sh", args: ["/home/vagrant/candig"]
  end

  config.vm.provider :openstack do |os, override|
    override.vm.synced_folder '.', '/home/vagrant/candig', type: 'virtualbox', disabled: true
    override.ssh.username = 'ubuntu'
    override.ssh.private_key_path = ENV["OS_PRIVATEKEY_PATH"]
    os.username = ENV["OS_USERNAME"]
    os.password = ENV["OS_PASSWORD"]
    os.user_domain_name = ENV["OS_USER_DOMAIN_NAME"]
    os.project_name = ENV["OS_PROJECT_NAME"]
    os.project_domain_name = ENV["OS_PROJECT_DOMAIN_ID"]
    os.identity_api_version = ENV["OS_IDENTITY_API_VERSION"]
    os.region = ENV["OS_REGION_NAME"]
    os.openstack_auth_url = ENV["OS_AUTH_URL"]
    os.interface_type = ENV["OS_INTERFACE"]
    os.keypair_name       = ENV["OS_KEYPAIR"]
    
    os.flavor             = 'm1.large'
    os.image              = 'UbuntuServer-1804-2019Nov20'
    os.server_name        = 'candig-vagrant'
    override.vm.provision 'shell', privileged: false, path: "provision.sh", args: ["."]
    override.vm.provision :reload
    override.vm.provision 'shell', privileged: false, path: "setup_containers.sh", args: ["/home/ubuntu/CanDIGv2"]
  end
end
