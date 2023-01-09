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
 ├── docs/                         - documentation, installation instructions
 ├── etc/                          - contains misc files/config/scripts
 │    ├── docker/                  - docker configurations
 │    ├── env/                     - sample .env file
 |    ├── tests/                   - integration tests (under development)
 ├── lib/                          - contains modules of servies/apps
 └── tmp/                          - contains temporary files used for runtime functionality
      ├── configs/                 - config files that are added to services post-deployment
      ├── data/                    - local data for running services
      ├── federation/              - federation configuration files
      ├── tyk/                     - tyk configuration files
      ├── vault/                   - vault keys
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

  CANDIG_MODULES=minio htsget-server katsu candig-data-portal

Optional modules follow the `#` and include federation service, various monitoring components, workflow execution, and some older modules not generally installed.

For federated installations, you will need `federation-service`.

For production deployments, you will probably want to include  `federation-service weavescope logging monitoring`. Be aware that the last three require more resources, includeing storage.

Authorization and authentication modules defined in  `CANDIG_AUTH_MODULES` are only installed if you run `make init-authx` during deployment.

## `make` Deployment

To deploy CanDIGv2, follow the docker deployment guide in `docs/`:

* [Docker Deployment Guide](./docs/install-docker.md)

There are other deprecated deployment guides in `docs`, but there are no guarantees that these still function:

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
| Katsu (KATSU Metadata) | links  | DFD: `katsu`        |
| Federation Service     | links  | DFD: `federation_service`    |
| HTSGet                 | links  | DFD: `htsget_app`            |
| KATSU DRS              | links  | DFD: `katsu_drs`             |
| WES Server             | links  | DFD: `wes_server`            |
| CanDIG Data Portal     | links  | DFD: `candig-data-portal`    |
