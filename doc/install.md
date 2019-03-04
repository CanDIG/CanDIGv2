# CanDIG Install Guide
- - -

## Install OS Dependencies

### Debian

1. Update system/install dependencies

```bash
sudo apt update && \
  sudo apt dist-upgrade -y && \
  sudo apt autoclean && \
  sudo apt autoremove -y

sudo apt install -y git-core build-essential
```

2. Install Docker

```bash
# remove old versions (optional)
sudo apt-get remove docker docker-engine docker.io \
  containerd runc

sudo apt-get install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg2 \
  software-properties-common

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository \
  "deb [arch=amd64] https://download.docker.com/linux/debian \
  $(lsb_release -cs) \
  stable"

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io

sudo systemctl enable docker

sudo systemctl start docker

sudo usermod -aG docker `whoami`
```

### CentOS 7

1. Update system/install dependencies

```bash
sudo yum update

sudo yum install -y git-core

sudo yum groupinstall -y 'Development Tools'
```

2. Install Docker

```bash
# remove old versions (optional)
sudo yum remove -y docker \
  docker-client \
  docker-client-latest \
  docker-common \
  docker-latest \
  docker-latest-logrotate \
  docker-logrotate \
  docker-engine

sudo yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2

sudo yum-config-manager -y \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

sudo yum update

sudo yum install -y docker-ce docker-ce-cli containerd.io

sudo systemctl enable docker

sudo systemctl start docker

sudo usermod -aG docker $(whoami)`
```

## Install CanDIG Dependencies

1. Modify `.env` file

2. Create Cluster
```bash
# view helpful commands
make

# initialize
make init

# create images
make images

# deploy stack
make stack

```
