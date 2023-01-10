# CanDIGv2 Install Guide

---
These instructions work for server deployments or local linux deployments. For local OSX using M1 architecture, follow the [Mac Apple Silicon Installation](#mac-apple-silicon-installation) instructions at the bottom of this file. For WSL you can follow the linux instructions and follow WSL instructions for firewall file at [update firewall](#update-firewall).

Before beginning, you should set up your environment variables as described in the [README](README.md).

## Install OS Dependencies

### Debian

1. Update system/install dependencies

```bash
sudo apt update && \
  sudo apt dist-upgrade -y && \
  sudo apt autoclean && \
  sudo apt autoremove -y

sudo apt install -y git-core build-essential curl
sudo apt install -y libbz2-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
  libsqlite3-dev libssl-dev uuid-dev libreadline-dev \
  zlib1g-dev tk-dev libffi-dev python-dev

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
make bin-pyenv
exec bash
make init-pipenv
pipenv shell
```

##  Deploy CanDIGv2 Services with Compose

The `init-docker` command will initialize CanDIGv2 and set up docker networks, volumes, configs, secrets, and perform other miscellaneous actions needed before deploying a CanDIGv2 stack. Running `init-docker` will override any previous configurations and secrets.

```bash
# initialize docker environment
make init-docker

# Setup required local redirect
make init-hosts-file

# pull latest CanDIGv2 images (if you didn't create images locally)
make docker-pull

# deploy stack
make compose
make init-authx # If this command fails, try the #update-firewall section of this Markdown file
# TODO: post deploy auth configuration

```

## Update Firewall

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

# 6. remove virtualenv environment
make clean-pipenv
```

## Mac Apple Silicon Installation

### 1) Step1: Install Docker and Dependencies

Mac users can get [docker desktop](https://docs.docker.com/desktop/mac/apple-silicon/). Also installed rosetta and used Docker Compose V2 as suggested at the moment.

**Optional**: dependencies below are not required but might be needed (skip if you have)
  
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install md5sha1sum
brew install md5sha1sum

# Install PostgreSQL
brew install postgresql

# Install dependencies for pyenv
brew install openssl readline sqlite3 xz zlib
```

### Step 2: Initialize CanDIGv2 Repo

```bash
# 1. initialize repo and submodules
git clone -b develop https://github.com/CanDIG/CanDIGv2.git
cd CanDIGv2
git submodule update --init --recursive

# 2. copy and edit .env with your site's local configuration
cp -i etc/env/example.env .env
```

- Edit the .env file to specify Apple Sillicon platform:

```bash
# options are [linux, darwin, arm64mac]
VENV_OS=arm64mac
```

If you are using `bash`, do the following (not tested):

```bash
# 3. fetch binaries and initialize candig virtualenv
make bin-pyenv
exec $SHELL
make init-pipenv
```

If you are using `zsh`, do this instead:
```bash
# Install pyenv
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

# Set pyenv path in ~/.zshrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc

# Restart the shell to take effect
exec zsh

# Install python (find the version in .env VENV_PYTHON)
pyenv install 3.10.9

# Set python version for this directory (for example CanDIGv2 root folder):
pyenv local 3.10.9

# Install pipenv
pip install pipenv

# spawn the virtual environment
pipenv shell
```

### Step 3: Initialize CanDIGv2 (Docker)

- Make sure you are in `CanDIGv2` virtual environment (activate it in previous step)

```bash
make init-docker
make init-hosts-file # Setup required local redirect
```

### Step 4: Deploy CanDIGv2 Services (Compose)

```bash
make compose
```

### Step 5: Create Auth Stack

Edit the .env, comment out the jboss and use c3g version

```bash
# keycloak service
KEYCLOAK_VERSION=16.1.1
KEYCLOAK_BASE_IMAGE=quay.io/c3genomics/keycloak:${KEYCLOAK_VERSION}.arm64
# KEYCLOAK_BASE_IMAGE=jboss/keycloak:${KEYCLOAK_VERSION}
```

Then run `make`:

```bash
make init-authx
make compose-authx
```

Once everything has run without errors, take a look at the documentation for
[ingesting data and testing the deployment](ingest-and-test.md) as well as
[how to modify code and test changes](docker-and-submodules.md) in
the context of the CanDIG stack.
