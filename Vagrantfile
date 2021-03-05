# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'debian/contrib-buster64'
  config.vm.hostname = 'candig.local'
  # config.vm.network "forwarded_port", guest: 80, host: 80
  # config.vm.network "forwarded_port", guest: 443, host: 443
  config.vm.synced_folder '.', '/vagrant', type: 'virtualbox'

  config.vm.provider 'virtualbox' do |vb|
    vb.name = 'candig-dev'
    vb.gui = false
    vb.customize ['modifyvm', :id, '--cpus', 4]
    vb.customize ['modifyvm', :id, '--memory', '4096']
  end

  # run custom shell on provision
  config.vm.provision 'shell', privileged: false, inline: <<-SHELL
    sudo apt-get update
    sudo apt-get upgrade -y

    sudo apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget curl git
    sudo apt-get install -y libsqlite3-dev libbz2-dev liblzma-dev lzma sqlite3
    sudo apt-get install -y apt-transport-https ca-certificates gnupg2 software-properties-common

    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io

    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $(whoami)

    sudo chown -R $(whoami):$(whoami) /vagrant
  SHELL
end
