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

## Initialize CanDIGv2 Repo

```bash
# 1. initialize repo and submodules
git clone -b stable https://github.com/CanDIG/CanDIGv2.git
git submodule update --init --recursive

# 2. copy and edit .env with your site's local configuration
cp -i etc/env/example.env .env

# 3. fetch binaries and initialize candig virtualenv
make bin-all
make init-conda
source etc/venv/activate.sh
```

## Create CanDIGv2 Development VM

Using the provided steps will help to create a `docker-machine` cluster on VirtualBox. The `make` CLI can also be used to provision and connect a multi-vm Swarm cluster. Users are encouraged to use this docker environment for CanDIGv2 development as it provides an isolated domain from the host environment, increasing security and reducing conflicts with host processes. Modify the `MINIKUBE_*` options in `.env`, then launch a single-node or multi-node `docker-machine` with `make machine-$vm_name`, where `$vm_name` is a unique vm name.

To build a development swarm cluster run the following:

* create a swarm manager with `make machine-manager`, additional nodes with `make machine-manager2`...
* create a swarm worker with `make machine-worker`, additional nodes with `make machine-worker2`...

To switch your local docker-client to use `docker-machine`, run `eval $(bin/docker-machine env manager)`. Add this line into `bashrc`  with `bin/docker-machine env manager >> $HOME/.bashrc` in order to set `docker-machine` as the default `$DOCKER_HOST` for all shells.

You can move on to the initialize instructions for Docker.

## Initialize CanDIGv2 (Docker)

The following commands will initialize CanDIGv2 and set up docker networks, volumes, configs, secrets, and perform other miscellaneous actions needed before deploying a CanDIGv2 stack. Only perform these actions once as it will override any previous configurations and secrets. Once completed, you can deploy a Compose or Swarm stack.

```bash
# initialize docker environment
make init-docker
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
docker login
make docker-push
```

## Deploy CanDIGv2 Services (Swarm)
> Note: swarm deployment requires minimum 2 nodes connected (1 manager, 1 worker)

1. Create initial manager node

```bash
eval $(bin/docker-machine env manager)
make init-swarm
```

2. Add additional manager/worker nodes

```bash
# set the SWARM_MODE and SWARM_MANAGER_IP in .env
eval $(bin/docker-machine env worker)
make swarm-join
```

3. Deploy CanDIGv2 stack on the docker swarm

```bash
eval $(bin/docker-machine env manager)

# check cluster status (READY:ACTIVE)
docker node ls

# deploy CanDIGv2 services
make stack
```

## Cleanup CanDIGv2 Compose/Swarm Environment

Use the following steps to clean up running CanDIGv2 services in a docker-compose configuration. Note that these steps are destructive and will remove **ALL** containers, secrets, volumes, networks, certs, and images. If you are using docker in a shared environment (i.e. with other non-CanDIGv2 containers running) please consider running the cleanup steps manually instead.

The following steps are performed by `make clean-all`:

```bash
# 1. stop and remove running stacks
make clean-stack
make clean-compose

# 2. stop and remove remaining containers
make clean-containers

# 3. remove all configs/secrets from docker and local dir
make clean-secrets
make clean-configs

# 4. remove all docker volumes and local data dir
make clean-volumes

# 5. remove all unused networks
make clean-networks

# 6. delete all cached images
make clean-images

# 7. leave swarm-cluster
make clean-swarm

# 8. destroy all docker-machine instances
make clean-machines

# 9. remove selfsigned-certs (including root-ca)
make clean-certs

# 10. remove conda environment
make clean-conda

# 11. remove bin dir (inlcuding miniconda)
make clean-bin
```

