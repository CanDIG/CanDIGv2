# CanDIGv2 Install Guide

These instructions work for server deployments or local linux deployments. For local OSX using M1 architecture, there are modification instructions in the [install-os-dependencies](#install-os-dependencies) section. For WSL you can follow the linux instructions and follow WSL instructions for firewall file at [update firewall](#update-firewall).

Docker Engine (also known as Docker CE) is recommended over Docker Desktop for linux installations.

Note that CanDIG requires **Docker Compose v2**, which is provided alongside the latest version of Docker Engine. Versions of Docker which do not provide Docker Compose will unfortunately not work with CanDIG.

Docker Engine (also known as Docker CE) is recommened over Docker Desktop for linux installations.

Note that CanDIG requires **Docker Compose v2**, which is provided alongside the latest version of Docker Engine. Versions of Docker which do not provide Docker Compose will unfortunately not work with CanDIG.

## Resource requirements

We have successfully run and installed the CanDIGv2 stack on VMs with 4 CPUs and 8GB of memory.

We recommend giving Docker at least 4 CPUs and 4GB of memory.

## Production vs Development Environments

CanDIG can be installed and deployed as below for development situations where no real data will ever be ingested into the system. For critical differences in production deployments, please see the [Guide to CanDIG production deployments](production-candig.md).

## Install OS Dependencies

<details>
<summary>Debian</summary>

1. Update system/install dependencies

```bash
sudo apt update && \
  sudo apt dist-upgrade -y && \
  sudo apt autoclean && \
  sudo apt autoremove -y

sudo apt install -y git-core build-essential
```
yq >= 4 is required.  See [https://github.com/mikefarah/yq/#install](https://github.com/mikefarah/yq/#install) for install options.

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

</details>

<details>

<summary>Ubuntu</summary>

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

yq >= 4 is required.  The apt version is outdated.  So:
```bash
sudo apt install snapd
sudo snap install yq
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

</details>

<details>

<summary>CentOS 7</summary>

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
yq >= 4 is required.  See [https://github.com/mikefarah/yq/#install](https://github.com/mikefarah/yq/#install) for install options.

</details>

<details>

<summary>Note for WSL Systems</summary>

Miniconda3 must be installed at `~/miniconda3` on WSL systems to avoid an infinite symlink loop. Add `CONDA_INSTALL = ~/miniconda3`  above `CONDA = $(CONDA_INSTALL)/bin/conda` in the Makefile to avoid this issue. You can also use the below command to move the miniconda3 installation to the correct location.

```bash
bash bin/miniconda_install.sh -f -b -u -p ~/miniconda3
```

yq >= 4 is required, but the conda version is outdated.  Install the latest version system-wide by following the instructions at [the yq GitHub](https://github.com/mikefarah/yq/#install).

</details>

<details>

<summary>For Apple Silicon</summary>

### 1. Install OS Dependencies

- Install dependencies

```bash
brew install gettext
brew link --force gettext
brew install jq
brew install yq
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

</details>

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

<details>

<summary>More info about the `.env` Environment File</summary>

You need an `.env` file in the project root directory, which contains a set of global variables that are used as reference to the various parameters, plugins, and config options that operators can modify for testing purposes. This repo contains an example `.env` file in `etc/env/example.env`.

For a basic desktop sandbox setup, the example variable file needs very little (if any) modification.

When deploying CanDIGv2
using `make`, `.env` is imported by `make` and all uncommented variables are added as environment variables via
`export`.

Some of the functionality that is controlled through `.env` are:

* operating system flags
* change docker network, driver, and swarm host
* modify ports, protocols, and plugins for various services
* version control and app pinning
* pre-defined defaults for turnkey deployment

Environment variables defined in the `.env` file can be read in `docker-compose` scripts through the variable substitution operator
`${VAR}`.

```yaml
# example compose YAML using variable substitution with default option
services:
  consul:
    image: progrium/consul
    network_mode: ${DOCKER_MODE}
...
```

</details>

<details>

<summary>Configuring CanDIG modules</summary>

Not all CanDIG modules are required for a minimal installation. The `CANDIG_MODULES` setting defines which modules are included in the deployment.

By default (if you copy the sample file from `etc/env/example.env`) the installation includes the minimal list of modules:

```
  CANDIG_MODULES=logging keycloak vault redis postgres htsget katsu query tyk opa federation candig-ingest candig-data-portal
```

Optional modules follow the `#` and include various monitoring components, workflow execution, and some older modules not generally installed.
 </details>

`install-all` will perform all of the steps to deploy CanDIG including the conda install, building images explicitly. **Note**: On Mac M1, you will not be able to use make install-all; instead, use the conda installation instructions as described above. Build-all will then build and compose the containers for you.


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


## Update Firewall

If the command still fails, it may be necessary to disable your local firewall, or edit it to allow requests from all ports used in the Docker stack.

Edit your firewall settings to allow connections from those adresses:

```bash
export DOCKER_BRIDGE_IP=$(docker network inspect bridge | grep Subnet | awk '{print $2}' | tr -d ',')
sudo ufw allow from $DOCKER_BRIDGE_IP to <your ip>
```

Re-run `make clean-authx` and `make init-authx` and it should work.



Once everything has run without errors, take a look at the documentation for
[ingesting data and testing the deployment](ingest-and-test.md) as well as
[how to modify code and test changes](docker-and-submodules.md) in
the context of the CanDIG stack.
