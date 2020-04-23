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

sudo usermod -aG docker $(whoami)
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

sudo usermod -aG docker $(whoami)
```

## Install gVisor (Optional)

```bash
wget https://storage.googleapis.com/gvisor/releases/nightly/latest/runsc
wget https://storage.googleapis.com/gvisor/releases/nightly/latest/runsc.sha512
sha512sum -c runsc.sha512
chmod a+x runsc
sudo mv runsc /usr/local/bin
rm runsc.sha512

sudo mkdir -p /etc/docker

# change storage-driver to overlay2 if OS does not use BTRFS filesystem
# change network portion (x.x.0.1/16) of bip if subnet is already used in local network
# change platform for runsc to kvm if kvm on available on host or guest VM is not KVM
# change network from sandbox to host if you want to use host network stack
# change runsc overlay to true if you want to persist modifications to running containers

sudo bash -c 'cat > /etc/docker/daemon.json << EOF
{
  "storage-driver": "overlay2",
  "bip": "11.11.0.1/16",
  "features": {
    "buildkit": true
  },
  "runtimes": {
    "runsc": {
      "path": "/usr/local/bin/runsc",
        "runtimeArgs": [
          "--platform=ptrace",
          "--network=sandbox",
          "--overlay=false"
        ]
    }
  }
}
EOF'

sudo systemctl restart docker
```

## Install CanDIG Dependencies

1. Clone/pull latest CanDIGv2 repo from `https://github.com/CanDIG/CanDIGv2.git`

2. Create/modify `.env` file
  * `cp -i etc/env/compose.env .env`
  * Edit `.env` with your site's local configuration

3. Create Cluster
```bash
# view helpful commands
make

# initialize
make init-docker

# create images
make images

# deploy stack (if using docker-compose environment)
make compose

# deploy stack (if using docker swarm environment)
make stack
```
