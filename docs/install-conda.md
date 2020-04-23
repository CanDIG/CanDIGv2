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

sudo apt install -y git-core build-essential screen
```

### CentOS 7

1. Update system/install dependencies

```bash
sudo yum update

sudo yum install -y git-core screen

sudo yum groupinstall -y 'Development Tools'
```

## Install CanDIG Dependencies

1. Clone/pull latest CanDIGv2 repo from `https://github.com/CanDIG/CanDIGv2.git`

2. Create/modify `.env` file
  * `cp -i etc/env/conda.env .env`
  * Edit `.env` with your site's local configuration

3. Create CanDIG Daemons
```bash
# view helpful commands
make

# initialize
make init-conda

# source miniconda3
source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh

# run candig services in screen terminals
make conda
```
