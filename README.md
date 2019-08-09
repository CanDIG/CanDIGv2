# CanDIG v2 PoC
- - -

## Overview

The CanDIG v2 project is a collection of heterogeneos services designed to work together to facilitate end to end
dataflow for genomic data.

## Project Structure

```plaintext
CanDIGv2/
  ├── .env                        ├ global variables
  ├── site.env                    ├ global overrides
  ├── Makefile                    ├ actions for repeatable testing/deployment
  ├── bin/                        ├ local binaries directory
  ├── doc/                        ├ documentation for various aspects of CanDIGv2
  ├── etc/                        ├ contains misc files/config/scripts
  │   ├── docker/                 ├ docker configurations
  │   ├── env/                    ├ sample env files for site.env
  │   ├── ssl/                    ├ ssl rootCA/site configs and certs
  │   ├── venv/                   ├ dependency files for virtualenvs (conda, pip, etc.)
  │   └── yml/                    ├ various yaml based configs (toil, traefik, etc.)
  └── lib/                        ├ contains modules of servies/apps
     ├── compose/                 ├ set of base docker variables for Compose
     ├── kubernetes/              ├ set of base docker variables for Kubernetes
     ├── swarm/                   ├ set of base docker variables for Swarm
     └── ga4gh-dos/               ├ example module, folder name = module name (i.e. make compose-ga4gh-dos)
          ├── docker-compose.yml  ├ minimum requirement of module, contains deployment context
          └── Dockerfile          ├ contains build context for module
```

## `.env` Environment File

The `.env` file in the project root directory contains a set of global variables that are used as reference to
the various parameters, plugins, and config options that operators can modify for testing purposes.

Some of the functionality that is controlled through `.env` are:
  * change docker network, driver, and swarm host
  * modify ports, protocols, and plugins for various services
  * version control and app pinning
  * pre-defined defaults for turnkey deployment

Compose supports declaring default environment variables in an environment file named `.env` placed in the folder
where the `docker-compose` command is executed (current working directory). Similarly, when deploying CanDIGv2
using `make`, `.env` is imported by `make` and all uncommented variables are added as environment variables via
`export`.

These evironment variables can be read in `docker-compose` scripts through the variable substitution operator
`${VAR:-default}`.

```yaml
# example compose YAML using variable substitution with default option
services:
  consul:
    image: progrium/consul
    network_mode: ${DOCKER_MODE:-bridge}
...
```

### `site.env` Site Overrides

The `site.env` file is an easy way to keep a set of overrides for the various parameters contained in `.env`. This file is read by `Makefile` and any corresponding values will override the global default for CanDIGv2. Site operators are encouraged to keep changes in `site.env` rather than in `.env` directly, as `.env` may be modified from time-to-time by the CanDIG development team. The `site.env` will always override the same global export value for `.env`. Please note that `site.env` will not be saved with repo by default (blocked in `.gitignore`). This is by design to allow developers to test different configurations of CanDIGv2.

## `make` Deployment

```bash
# view available options
make

# create python virtualenv for docker-compose and HPC
make virtualenv

# initialize docker and create required docker networks
make init

# initialize docker-compose environment
make init-compose

# initialize hpc environment
make init-hpc

# initialize kubernetes environment
make init-kubernetes

# initialize docker-swarm environment (alias for swarm-init)
make init-swarm

# create docker bridge networks
make docker-net

# push docker images to CanDIG repo
make docker-push

# create docker secrets for CanDIG services
make docker-secrets

# create persistant volumes for docker containers
make docker-volumes

# get all package binaries
make bin-all

# download kubectl (for kubernetes deployment)
make bin-kubectl

# download latest minikube binary from Google repo
make bin-minikube

# download minio server/client
make bin-minio

# generate secrets for minio server/client
make minio-secrets

# start minio server instance
make minio-server

# create minikube environment for (kubernetes) integration testing
make minikube

# generate root-ca and site ssl certs using openssl
make ssl-cert

# initialize primary docker-swarm master node
make swarm-init

# join a docker swarm cluster using manager/worker token
make swarm-join

# create docker swarm compatbile secrets
make swarm-secrets

# (re)build service image for all modules
make images

# create toil images using upstream Toil repo
make toil-docker

# deploy/test all modules in lib/ using docker-compose
make compose

# deploy/test all modules in lib/ using docker stack
make stack

# deploy/test all modules in lib/ using kubernetes
make kubernetes

# (re)build service image and deploy/test using docker-compose
# $module is the name of the sub-folder in lib/
module=htsget-server
make build-$module

# deploy/test individual modules using docker-compose
# $module is the name of the sub-folder in lib/
module=ga4gh-dos
make compose-$module

# deploy/test indivudual modules using docker stack
# $module is the name of the sub-folder in lib/
module=igv-js
make stack-$module

# run all cleanup functions
make clean-all

# cleanup docker stack(s)
clean-stack

# stop all running containers and remove all run containers
clean-containers

# clear swarm secrets
clean-secrets

# remove all peristant volumes
clean-volumes

# (foricibily) leave docker-swarm
clean-swarm

# clear bridge-net/traefik-net/agent-net
clean-networks

# clear all images (including base images)
clean-images

# cleanup for compose, preserves everything except services/containers
clean-compose

# cleanup for stack/kubernetes, preserves everything except stack/services/containers
clean-stack
```

