# CanDIGv2 Install Guide

---

These instructions work for server deployments or local linux deployments. For local OSX using M1 architecture, there are [modification instructions](#modifications-for-apple-silicon-m1) instructions at the bottom of this file. For WSL you can follow the linux instructions and follow WSL instructions for firewall file at [update firewall](#update-firewall).

Before beginning, you should set up your environment variables as described in the [README](../README.md).

Docker Engine (also known as Docker CE) is recommened over Docker Desktop for linux installations.

Note that CanDIG requires **Docker Compose v2**, which is provided alongside the latest version of Docker Engine. Versions of Docker which do not provide Docker Compose will unfortunately not work with CanDIG.


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

### Ubuntu

1. Update system/install dependencies
```bash
sudo apt-get update

sudo apt-get install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg2 \
  software-properties-common \
  apt-transport-https \
  ca-certificates curl \
  software-properties-common \
  make \
  gcc
```

2. Install Docker

Follow the [official Docker directions](https://docs.docker.com/engine/install/ubuntu/).  Installation using the [apt repository method](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) is recommended.

Set docker to run as a service on startup.
```bash
sudo systemctl enable docker 

sudo systemctl start docker
```
You may have to reboot (not just log out).

Add yourself to the docker group rather than use sudo all the time.
```bash
sudo usermod -aG docker $(whoami) 
```
You may have to log out or restart your shell for this setting to take effect.

Verify that you are a member of the `docker` group with:
```bash
groups
# or
getent group docker
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

### Note for WSL Systems
Miniconda3 must be installed at `~/miniconda3` on WSL systems to avoid an infinite symlink loop. Add `CONDA_INSTALL = ~/miniconda3`  above `CONDA = $(CONDA_INSTALL)/bin/conda` in the Makefile to avoid this issue. You can also use the below command to move the miniconda3 installation to the correct location.


```bash
bash bin/miniconda_install.sh -f -b -u -p ~/miniconda3
```

## Initialize CanDIGv2 Repo

```bash
# 1. initialize repo and submodules
git clone -b develop https://github.com/CanDIG/CanDIGv2.git
cd CanDIGv2
git submodule update --init --recursive

# 2. copy and edit .env with your site's local configuration
cp -i etc/env/example.env .env

# 3. (IF NOT USING MAKE INSTALL-ALL) option A: install miniconda and initialize candig virtualenv (use this option
# for systems installations). Installs miniconda in the candigv2 repo.
make bin-conda  # If this fails on WSL, see the Note for WSL Systems section below
make init-conda

# 3. (IF NOT USING MAKE INSTALL-ALL) option B: if you want to use an existing conda installation on your local
# at the top of the Makefile, set CONDA_BASE to your existing conda installation
make mkdir # skip most of bin-conda, but need the dir-creating step
make init-conda

# 4. Activate the candig virtualenv. It may be necessary to restart your shell before doing this
conda activate candig
```

## Deploy CanDIGv2 Services with Compose


### New

`install-all` will perform all of the steps of the old method (section below) including the conda install, building images explicitly. **Note**: On Mac M1, you will not be able to use make install-all; instead, use the conda installation instructions as described above. Build-all will then build and compose the containers for you.


```bash
make install-all
```

`build-all` will do the same without running bin-conda and init-conda:

```bash
make build-all
```

On some machines (MacOS), if you get an error something like:
```
Please ensure the value of $CANDIG_DOMAIN in your .env file points to this machine
This should either be: 1) your local IP address, as assigned by your local network, or
2) a domain name that resolves to this IP address
```
it may be necessary to add the following to `/etc/hosts`:

In a terminal, run the following commands
```
sudo nano /etc/hosts
```

Then add the following line at the bottom of the file and save the changes:

```
::1	candig.docker.internal
```

In some other cases, it may be necessary to add your local/internal (network) IP manually, if the build process complains that it could not find the right IP (`ERROR: Your internet adapter could not be found automatically.` or `ERROR: More than one IP has been detected.`). In this case, find out what your local IP address is 

```bash
# on mac
ifconfig en0 | awk '$1 == "inet" {print $2}'
# on linux
ip route | awk -F\  '/default/ {print $9}'
```

Then edit your .env file with:

```bash
LOCAL_IP_ADDR=<your local IP>
```
Where `<your local IP>` is your local network IP (e.g. 192.168.x.x)

If you can see the data portal at http://candig.docker.internal:5080/, your installation was successful.

Confirm your installation with the [automatic tests](/docs/ingest-and-test.md).


### Old
The `init-docker` command will initialize CanDIGv2 and set up docker networks, volumes, configs, secrets, and perform other miscellaneous actions needed before deploying a CanDIGv2 stack. Running `init-docker` will override any previous configurations and secrets.

```bash
# initialize docker environment
make init-docker

## Do one of the following:
# pull latest CanDIGv2 images:
make docker-pull

# or build images:
make build-images

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

# 6. remove bin dir (inlcuding miniconda)
make clean-bin
```

## For Apple Silicon

### 1. Install OS Dependencies

- Install dependencies

```bash
brew install gettext
brew link --force gettext 
```

- Get [Docker Desktop for Apple Silicon](https://docs.docker.com/desktop/install/mac-install/). Be sure to start it.

### 2. Initialize CanDIGv2 Repo

```bash
git clone -b develop https://github.com/CanDIG/CanDIGv2.git
cd CanDIGv2
git submodule update --init --recursive
cp -i etc/env/example.env .env
```

### 3. Update .env file

```bash
# find out your ip and add to LOCAL_IP_ADDR
LOCAL_IP_ADDR=xxx.xx.x.x
# change OS
VENV_OS=arm64mac
# change keycloak
KEYCLOAK_BASE_IMAGE=quay.io/c3genomics/keycloak:${KEYCLOAK_VERSION}.arm64
```

Edit /etc/hosts on the machine (`sudo nano /etc/hosts`):

```bash
::1 candig.docker.internal
```

### 4. Initialize conda

```bash
make bin-all
make init-conda
conda activate candig
```

### 5. Build and test

```bash
make build-all
make test-integration
```

Once everything has run without errors, take a look at the documentation for
[ingesting data and testing the deployment](ingest-and-test.md) as well as
[how to modify code and test changes](docker-and-submodules.md) in
the context of the CanDIG stack.
