# CanDIGv2 Install Guide

---

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

## Docker installation instructions for Ubuntu 22.04

```bash
sudo apt-get install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg2 \
  software-properties-common \
  apt-transport-https \
  ca-certificates curl \
  software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

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
git clone -b develop https://github.com/CanDIG/CanDIGv2.git
cd CanDIGv2
git submodule update --init --recursive

# 2. copy and edit .env with your site's local configuration
cp -i etc/env/example.env .env

# 3. fetch binaries and initialize candig virtualenv
make bin-all
make init-conda
```

## Choose Docker Deployment Strategy

We provide instructions below for two different docker deployment strategies. Option 1 uses `docker-compose` to deploy each module. Option 2 builds a Docker Swarm cluster using `docker-machine`. We use Option 2 for production, but Option 1 is simpler for local dev installation.

### Option 1: Deploy CanDIGv2 Services with Compose

The `init-docker` command will initialize CanDIGv2 and set up docker networks, volumes, configs, secrets, and perform other miscellaneous actions needed before deploying a CanDIGv2 stack. Running `init-docker` will override any previous configurations and secrets.

```bash
# initialize docker environment
make init-docker

# (optional) create images
make images

# pull latest CanDIGv2 images (if you didn't create images locally)
make docker-pull

# deploy stack
make compose
make init-authx
# TODO: post deploy auth configuration

# (optional) push updated images to $DOCKER_REGISTRY
docker login
make docker-push
```

## Option 2: Deploy CanDIGv2 using Docker Swarm

### Create CanDIGv2 Development VM

Using the provided steps will help to create a `docker-machine` cluster on VirtualBox. The `make` CLI can also be used to provision and connect a multi-vm Swarm cluster. Users are encouraged to use this docker environment for CanDIGv2 development as it provides an isolated domain from the host environment, increasing security and reducing conflicts with host processes. Modify the `MINIKUBE_*` options in `.env`, then launch a single-node or multi-node `docker-machine` with `make machine-$vm_name`, where `$vm_name` is a unique vm name.

To build a development swarm cluster run the following:

- create a swarm manager with `make machine-manager`, additional nodes with `make machine-manager2`...
- create a swarm worker with `make machine-worker`, additional nodes with `make machine-worker2`...

To switch your local docker-client to use `docker-machine`, run `eval $(bin/docker-machine env manager)`. Add this line into `bashrc` with `bin/docker-machine env manager >> $HOME/.bashrc` in order to set `docker-machine` as the default `$DOCKER_HOST` for all shells.

### Initialize CanDIGv2 (Docker)

The following commands will initialize CanDIGv2 and set up docker networks, volumes, configs, secrets, and perform other miscellaneous actions needed before deploying a CanDIGv2 stack. Only perform these actions once as it will override any previous configurations and secrets. Once completed, you can deploy a Compose or Swarm stack.

```bash
# initialize docker environment
make init-docker
```

### Deploy using Swarm

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

## Update hosts

Get your local IP address and edit your /etc/hosts file to add:

```bash
<your ip>  docker.localhost
<your ip>  auth.docker.localhost
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

# Mac Apple Silicon Installation

### 1) Step1: Install OS Dependencies

Mac users can get [docker desktop](https://docs.docker.com/desktop/mac/apple-silicon/). Also installed rosetta and used Docker Compose V2 as suggested at the moment.

- **Optional**: these installations are not mentioned but might be needed:
  - Install [brew](https://brew.sh/)
  - Install md5sha1sum (`brew install md5sha1sum`)
  - Install PostgreSQL (`brew install postgresql`)

### Step 2: Initialize CanDIGv2 Repo

```bash
# 1. initialize repo and submodules
git clone -b develop https://github.com/CanDIG/CanDIGv2.git
cd CanDIGv2
git submodule update --init --recursive

# 2. copy and edit .env with your site's local configuration
cp -i etc/env/example.env .env
```

- Edit the .env file:

```bash
# options are [<ip_addr>, <url>, host.docker.internal, docker.localhost]
CANDIG_DOMAIN=docker.localhost
CANDIG_AUTH_DOMAIN=docker.localhost
...
# options are [linux, darwin, arm64mac]
VENV_OS=arm64mac
VENV_NAME=candig
```

- Continue to run `make`

```bash
# 3. fetch binaries and initialize candig virtualenv
make bin-all
make init-conda
```

- To activate conda env, do the following:

```bash
conda env list
# Copy the whole path that contains `/envs/candig`
conda activate {path_to_folder}/CanDIGv2/bin/miniconda3/envs/candig
```

- Note: The reason we cannot activate it automatically on Mac was described in this [post](https://stackoverflow.com/questions/57527131/conda-environment-has-no-name-visible-in-conda-env-list-how-do-i-activate-it-a). If `conda env` is not in the root folder, it won't have a name.

### Step 3: Initialize CanDIGv2 (Docker)

- Make sure you are in `candig` virtual environment (activate it in previous step)

```bash
make init-docker
```

### Step 4: Deploy CanDIGv2 Services (Compose)

```bash
make compose
```

### Step 5: Update hosts

- Get the local IP address in the terminal:

```bash
ifconfig -l | xargs -n1 ipconfig getifaddr
```

- Then edit your /etc/hosts file:

```bash
sudo nano /etc/hosts
```

- Add the IP address to the end of the file so it look like this:

```bash
# Other settings
192.168.X.XX docker.localhost
```

### Step 6: Create Auth Stack

In the .env, comment out all the `WES_OPT+=…` (We don't use it right now)

```bash
# WES_OPT=--opt=extra=--batchSystem=Mesos
...
# WES_OPT+=--opt=extra=--metrics
```

The old keycloak image (15.0.0) is not compatible with M1, so we need to upgrade it.

Go to `lib/keycloak/docker-compose.yml` and replace the `- BASE_IMAGE=candig/keycloak:${KEYCLOAK_VERSION}` with one of the following:

```bash
- BASE_IMAGE=mihaibob/keycloak:18.0.2-legacy # (from StackOverflow)
# or 
- BASE_IMAGE=quay.io/c3genomics/keycloak:16.1.1.arm64 # (an alternative built on an M1, for an M1)
```

Then run `make`:

```bash
make init-authx
```

If you got this error:

```bash
Getting keycloak token
Traceback (most recent call last):
  File "<string>", line 1, in <module>
KeyError: 'access_token'
make: *** [init-authx] Error 1
```

Then try to replace all the `keycloak` passwords in `tmp/secrets` with something simple like `thisisasupersecretpassword`, basically no special chars.

Try `make clean-authx` and `make init-authx` and it should worked 🎉
