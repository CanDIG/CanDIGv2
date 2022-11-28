# CanDIG v2

- - -

## Overview

The CanDIG v2 project is a collection of heterogeneous services designed to work together to facilitate end to end
dataflow for genomic data.

## Project Structure

```plaintext
CanDIGv2/
 ├── .env                          - global variables
 ├── Makefile                      - functions for repeatable testing/deployment (Docker/Kubernetes)
 ├── tox.ini                       - functions for repeatable testing/deployment (Python Venv/Screen)
 ├── bin/                          - local binaries directory
 ├── docs/                         - documentation for various aspects of CanDIGv2
 ├── etc/                          - contains misc files/config/scripts
 │    ├── docker/                  - docker configurations
 │    ├── env/                     - sample env files for site.env
 │    ├── ssl/                     - ssl root-ca/site configs and certs
 │    ├── venv/                    - dependency files for virtualenvs (conda, pip, etc.)
 │    └── yml/                     - various yaml based configs (toil, traefik, etc.)
 ├── lib/                          - contains modules of servies/apps
 │    ├── compose/                 - set of base docker variables for Compose
 │    ├── kubernetes/              - set of base docker variables for Kubernetes
 │    ├── swarm/                   - set of base docker variables for Swarm
 │    ├── templates/               - set of template files used to create new module(s)
 │    └── ga4gh-dos/               - example module, folder name = module name (e.g. make compose-ga4gh-dos)
 │         ├── docker-compose.yml  - minimum requirement of module, contains deployment context
 │         ├── Dockerfile          - contains build context for module
 │         └── run.sh              - script which used for conda deployment (DEPRECATED)
 └── tmp/                          - contains temporary files used for runtime functionality
      ├── configs/                 - directory to store config files that are added to services post-deployment
      ├── data/                    - directory to store local data for running services
      └── secrets/                 - directory to store randomly generated secrets for service deployment
```

## `.env` Environment File

You need an `.env` file in the project root directory, which contains a set of global variables that are used as reference to
the various parameters, plugins, and config options that operators can modify for testing purposes. This repo contains an example `.env` file in `etc/env/example.env`.

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
### Configuring CanDIG modules

Not all CanDIG modules are required for a minimal installation. The `CANDIG_MODULES` and `CANDIG_AUTH_MODULES` define which modules are included in the deployment. 

By default (if you copy the sample file from `etc/env/example.env`) the installation includes the minimal list of modules:

  CANDIG_MODULES=minio htsget-server chord-metadata candig-server candig-data-portal

Optional modules follow the `#` and include federation service, various monitoring components, workflow execution, and some older modules not generally installed. 

For federated installations, you will need `federation-service`. 

For production deployments, you will probably want _add prod modules here_.

Authorization and authentication modules defined in  `CANDIG_AUTH_MODULES` are only installed if you run `make init-authx` during deployment. 

## `make` Deployment

To deploy CanDIGv2, follow the docker deployment guide in `docs/`:

* [Docker Deployment Guide](./docs/install-docker.md)

There are other deprecated deployment guides in `docs`, but there are no guarantees that these still function:

* [Vagrant Deployment Guide (with instructions for OpenStack)](./docs/install-vagrant.md)
* [Kubernetes Deployment Guide](./docs/install-kubernetes.md)
* [Tox Deployment Guide](./docs/install-tox.md)
* [Authentication and Authorization Deployment Guide](./docs/authx-setup.md)

View additional Makefile options with `make help`.

## Services and Components

### Add new service

New services can be added under `lib` directory.  Please refer to the
[template for new services README](./lib/templates/README.md) for more details.

### List of services

The following table lists the details from the Data Flow Diagram in the "Overview" section.

| Service/Component Name | Source | Notes                        |
|------------------------|--------|------------------------------|
| Katsu (CHORD Metadata) | links  | DFD: `chord_metadata`        |
| CNV Service            | links  | DFD: `cnv_service`           |
| Authorization Service  | links  | DFD: `authorization_service` |
| Federation Service     | links  | DFD: `federation_service`    |
| Datasets Service       | links  | DFD: `datasets_service`      |
| RNAGet                 | links  | DFD: `rnaget`                |
| CanDIGv1 Server        | links  | DFD: `candig_server`         |
| HTSGet                 | links  | DFD: `htsget_app`            |
| CHORD DRS              | links  | DFD: `chord_drs`             |
| IGV JS                 | links  | DFD: `igv_js`                |
| WES Server             | links  | DFD: `wes_server`            |
| CanDIG Data Portal     | links  | DFD:                         |