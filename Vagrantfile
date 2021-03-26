# -*- mode: ruby -*-
# vi: set ft=ruby :

# Install vagrant-disksize to allow resizing the vagrant box disk.
unless Vagrant.has_plugin?("vagrant-disksize")
    raise  Vagrant::Errors::VagrantError.new, "vagrant-disksize plugin is missing. Please install it using 'vagrant plugin install vagrant-disksize' and rerun 'vagrant up'"
end

Vagrant.configure('2') do |config|
  config.vm.provider 'virtualbox' do |vb|
    config.vm.hostname = 'candig.local'
    config.disksize.size = '50GB'
    config.vm.box = 'debian/contrib-buster64'
#     config.vm.network "forwarded_port", guest: 80, host: 80
#     config.vm.network "forwarded_port", guest: 443, host: 443
    config.vm.synced_folder '.', '/home/vagrant/candig', type: 'virtualbox'
    vb.name = 'candig-dev'
    vb.gui = false
    vb.customize ['modifyvm', :id, '--cpus', 4]
    vb.customize ['modifyvm', :id, '--memory', '4096']
  end

  config.vm.provider :openstack do |os|
    config.ssh.username = 'ubuntu'
    config.ssh.private_key_path = '/Users/daisie/.ssh/id_rsa'
    os.username = ENV["OS_USERNAME"]
    os.password = ENV["OS_PASSWORD"]
    os.user_domain_name = ENV["OS_USER_DOMAIN_NAME"]
    os.project_name = ENV["OS_PROJECT_NAME"]
    os.project_domain_name = ENV["OS_PROJECT_DOMAIN_ID"]
    os.identity_api_version = ENV["OS_IDENTITY_API_VERSION"]
    os.region = ENV["OS_REGION_NAME"]
    os.openstack_auth_url = ENV["OS_AUTH_URL"]
    os.interface_type = ENV["OS_INTERFACE"]

    os.keypair_name       = 'daisieh'
    os.flavor             = 'm1.large'
    os.image              = 'UbuntuServer-1804-2019Nov20'
    os.floating_ip_pool   = 'OS DMZ External 205.189.58.128/27'
    os.server_name        = 'daisieh'
  end


  # run custom shell on provision
  config.vm.provision 'shell', privileged: false, path: "provision.sh", args: ["/home/vagrant/candig"]
end
