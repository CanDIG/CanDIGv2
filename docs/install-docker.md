# CanDIGv2 Install Guide

---
These instructions work for server deployments or local linux deployments. For local OSX using M1 architecture, follow the [Mac Apple Silicon Installation](#mac-apple-silicon-installation) instructions at the bottom of this file. For WSL you can follow the linux instructions and follow WSL instructions for hosts file at [update hosts](#update-hosts).

Before beginning, you should set up your environment variables as described in the [README](README.md).

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
git clone -b develop https://github.com/CanDIG/CanDIGv2.git
cd CanDIGv2
git submodule update --init --recursive

# 2. copy and edit .env with your site's local configuration
cp -i etc/env/example.env .env

# 3. initialize candig virtualenv
source ./activate.sh
```

 ## Update hosts

Get your local IP address and edit your `/etc/hosts` file to add (note that the key and value are tab-delimited):

```bash
<your ip>  docker.localhost
<your ip>  auth.docker.localhost
```

### WSL
Edit your /etc/hosts file as stated above along with your Windows hosts file by adding your Windows IPv4 to both hosts files. This can be found at `C:\Windows\system32\drivers\etc`. How you edit this file will change between versions of Windows.

##  Deploy CanDIGv2 Services with Compose

The `init-docker` command will initialize CanDIGv2 and set up docker networks, volumes, configs, secrets, and perform other miscellaneous actions needed before deploying a CanDIGv2 stack. Running `init-docker` will override any previous configurations and secrets.

```bash
# initialize docker environment
make init-docker

# pull latest CanDIGv2 images (if you didn't create images locally)
make docker-pull

# deploy stack
make compose
make init-authx # If this command fails, try the #update-hosts section of this Markdown file
# TODO: post deploy auth configuration

```

If the command still fails, it may be necessary to disable your local firewall, or edit it to allow requests from all ports used in the Docker stack.

Edit your firewall settings to allow connections from those adresses:
```bash
export DOCKER_BRIDGE_IP=$(docker network inspect bridge | grep Subnet | awk '{print $2}' | tr -d ',')
sudo ufw allow from $DOCKER_BRIDGE_IP to <your ip>
```

Re-run `make clean-authx` and `make init-authx` and it should work.

## Cleanup CanDIGv2 Compose Environment

Use the following steps to clean up running CanDIGv2 services in a docker-compose configuration. Note that these steps are destructive and will remove **ALL** containers, secrets, volumes, networks, certs, and images. If you are using docker in a shared environment (i.e. with other non-CanDIGv2 containers running) please consider running the cleanup steps manually instead.

The following steps are performed by `make clean-all`:

```bash
# 1. stop and remove running stacks
make clean-compose

# 2. stop and remove remaining containers
make clean-containers

# 3. remove all configs/secrets from docker and local dir
make clean-secrets

# 4. remove all docker volumes and local data dir
make clean-volumes

# 5. delete all cached images
make clean-images

# 6. remove conda environment
make clean-conda

# 7. remove bin dir (inlcuding miniconda)
make clean-bin
```

## Mac Apple Silicon Installation

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
# options are [linux, darwin, arm64mac]
VENV_OS=arm64mac
VENV_NAME=candig
```

- Continue to run `make`

```bash
# 3. fetch binaries and initialize candig virtualenv
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

- Add the IP address to the end of the file so it look like this (noting that the key and value need to be tab-delimited):

```bash
# Other settings
192.168.X.XX docker.localhost
```

### Step 6: Create Auth Stack

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

Once everything has run without errors, take a look at the documentation for
[ingesting data and testing the deployment](ingest-and-test.md) as well as
[how to modify code and test changes](docker-and-submodules.md) in
the context of the CanDIG stack.
