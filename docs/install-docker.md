# CanDIGv2 Install Guide

---

These instructions work for server deployments or local linux deployments. For local OSX using M1 architecture, there are [modification instructions](#modifications-for-apple-silicon-m1) instructions at the bottom of this file. For WSL you can follow the linux instructions and follow WSL instructions for firewall file at [update firewall](#update-firewall).

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

# 3. option A: install miniconda and initialize candig virtualenv (use this option
# for systems installations). Installs miniconda in the candigv2 repo. 
make bin-conda  # If this fails on WSL, see the Note for WSL Systems section below
make init-conda

# 3. option B: if you want to use an existing conda installation on your local
# at the top of the Makefile, set CONDA_BASE to your existing conda installation
make mkdir # skip most of bin-conda, but need the dir-creating step 
make init-conda

# 4. Activate the candig virtualenv. It may be necessary to restart your shell before doing this
conda activate candig
```

### Note for WSL Systems
Miniconda3 must be installed at `~/miniconda3` on WSL systems to avoid an infinite symlink loop:

```bash
bash bin/miniconda_install.sh -f -b -u -p ~/miniconda3
```

## Deploy CanDIGv2 Services with Compose

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

# Specific cached modules may be out of date, so to disable caching for a specific module, add BUILD_OPTS='--no-cache' at the end of make like so:
# make build-htsget-server BUILD_OPTS='--no-cache'
# make compose-htsget-server
# make build-% and compose-% will work for any folder name in lib/

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

# 6. remove conda environment
make clean-conda

# 7. remove bin dir (inlcuding miniconda)
make clean-bin
```

## Modifications for Apple Silicon M1

There are some modifications that you need to make to install on M1 architecture. These are not full instructions, but only the changes from the standard install. 

### M1 environment variables

- In your .env file, set the M1 architecture:

```bash
# options are [linux, darwin, arm64mac]
VENV_OS=arm64mac
```

- Replace the default KEYCLOAK_BASE_IMAGE from jboss and use a compatible version from c3genomics:

```bash
# keycloak service
KEYCLOAK_VERSION=16.1.1
KEYCLOAK_BASE_IMAGE=quay.io/c3genomics/keycloak:${KEYCLOAK_VERSION}.arm64
# KEYCLOAK_BASE_IMAGE=jboss/keycloak:${KEYCLOAK_VERSION}
```


### Step 1 mods: Install Docker and Dependencies

Install [docker desktop](https://docs.docker.com/desktop/mac/apple-silicon/). 

**Optional**: Install the following packages with homebrew (or your favourite package manager). Depending on your local setup, you may also need rosetta and Docker Compose V2.

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install md5sha1sum
brew install md5sha1sum

# Install PostgreSQL
brew install postgresql

```

### Step 5: Create Auth Stack

- Update the opa image in `lib/opa/docker-compose.yml` to something arm-compatible (most of the `static` ones are. 

```bash
    opa:
        image: openpolicyagent/opa:edge-static
```


Once everything has run without errors, take a look at the documentation for
[ingesting data and testing the deployment](ingest-and-test.md) as well as
[how to modify code and test changes](docker-and-submodules.md) in
the context of the CanDIG stack.
