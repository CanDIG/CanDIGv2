# CanDIGv2 Install Guide

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

## Install gVisor (Deprecated)

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

## Install CanDIGv2 Dependencies

1. Clone/pull latest CanDIGv2 code from `https://github.com/CanDIG/CanDIGv2.git`

2. Create/modify `.env` file

* `cp -i etc/env/example.env .env`
* Edit `.env` with your site's local configuration

## Create CanDIGv2 Cluster

```bash
# view helpful commands
make

# initialize
make init-docker

# activate conda
source ./bin/miniconda3/etc/profile.d/conda.sh
conda activate $VENV_NAME
pip install -r ./etc/venv/requirements.txt
```

## Deploy CanDIGv2 Services (Compose)

```bash
# create images (optional)
make images

# pull latest CanDIGv2 images (instead of make images)
make docker-pull

# deploy stack (if using docker-compose environment)
make compose

# push updated images to $DOCKER_REGISTRY (optional)
docker login && make docker-push
```

## Deploy CanDIGv2 Services (Swarm)

```bash
# deploy stack (if using docker-swarm environment)
# requires minimum 2 nodes connected (1 manager, 1 worker)

# create initial manager node
make init-swarm

# add additional manager/worker nodes
make swarm-join

# check cluster status (READY:ACTIVE)
docker node ls

# deploy CanDIGv2 services
make stack
```

## Cleanup CanDIG Compose Environment

Use the following steps to clean up running CanDIGv2 services in a docker-compose configuration. *Note* that these steps are destructive and will remove *ALL* containers, secrets, volumes, networks, and images. If you are using docker in a shared environment (i.e. with other non-CanDIGv2 containers running) please consider running the cleanup steps manually instead.

The following steps are performed by `make clean-all`:

```bash
# 1. stop and remove running stacks
make clean-stack

# 2. stop and remove remaining containers
make clean-containers

# 3. remove all secrets from docker and local dir
make clean-secrets

# 4. remove all docker volumes
make clean-volumes

# 5. leave swarm-cluster
make clean-swarm

# 6. remove all unused networks
make clean-networks

# 7. delete all cached images
make clean-images

# 8. remove selfsigned-certs (including root ca)
make clean-certs

# 9. remove conda environment
make clean-conda

# 10. remove bin dir (inlcuding miniconda)
make clean-bin
```
