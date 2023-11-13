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
 ├── docs/                         - documentation, installation instructions
 ├── etc/                          - contains misc files/config/scripts
 │    ├── docker/                  - docker configurations
 │    ├── env/                     - sample .env file
 │    ├── ssl/                     - ssl root-ca/site configs and certs
 |    ├── tests/                   - integration tests (under development)
 │    ├── venv/                    - dependency files for virtualenvs (conda, pip, etc.)
 │    └── yml/                     - various yaml based configs (toil, traefik, etc.)
 ├── lib/                          - contains modules of services/apps
 └── tmp/                          - contains temporary files used for runtime functionality
      ├── configs/                 - config files that are added to services post-deployment
      ├── data/                    - local data for running services
      ├── federation/              - federation configuration files
      ├── tyk/                     - tyk configuration files
      ├── vault/                   - vault keys
      └── secrets/                 - directory to store randomly generated secrets for service deployment
```

## List of Services and Components

The following table lists the individual repos for each service and helper library developed by the CanDIG team that contribute to the CanDIGv2 stack.

| Service/Component Name    | Source                                                                | Description                       |
|---------------------------|-----------------------------------------------------------------------|------------------------------|
| authx                     | [`candigv2-authx`](https://github.com/CanDIG/candigv2-authx)          | Library to facilitate interacting with AuthZ/AuthN services, Keycloak, Tyk, Opa, Vault & Access to minIO S3 objects | 
| CanDIG Data Portal        | [`candig-data-portal`](https://github.com/CanDIG/candig-data-portal)  | Front-end User interface for CanDIG Services |
| CanDIGv2 Ingest Service     | [`candig-ingest`](https://github.com/CanDIG/candigv2-ingest)        | Ingests clinical and genomic data into the CanDIG infrastructure. As at September 2023, still being integrated into the stack. |
| Clinical ETL Code         | [`clinical_ETL_code`](https://github.com/CanDIG/clinical_ETL_code)    | Code to convert spreadsheet format into the MoH data model in preparation for ingest into `katsu` |
| Federation Service        | [`federation-service`](https://github.com/CanDIG/federation_service)  | Distributes requests across each federated node of the distributed infrastructure   |
| HTSGet                    | [`htsget_app`](https://github.com/CanDIG/htsget_app)                  | Implementation of GA4GH htsget API which ingests and indexes VCF files and stores GA4GH DRS objects for retrieval |
| Katsu                     | [`katsu`](https://github.com/CanDIG/katsu)                            | Manages the clinical metadata in a PostgreSQL database |
| CanDIG OPA                | [`candig-opa`](https://github.com/CanDIG/candig-opa)                  | Manages role-based access policies   |
| Query service             | [`query`](https://github.com/CanDIG/query)                            | as at September 2023, still being integrated into the stack |

As well as in-house developed services, the CanDIG stack relies on external software which is configured to work within the stack, configurations are found in the [`/lib`](/lib) folder for each software, these include:

| Service/Component Name                  | Role                                 |  
|-----------------------------------------|--------------------------------------|
| [Keycloak](https://www.keycloak.org/)   | Authentication management            |
| [minio](https://min.io/)                | Object storage for genomic files     |
| [OPA](https://www.openpolicyagent.org/) | Manages role-based access policies   |
| [Tyk](https://tyk.io/)                  | API management and redirection       |
| [Vault](https://www.vaultproject.io/)   | Secret and password management       |

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

```
  CANDIG_MODULES=minio htsget-server katsu candig-data-portal
```

Optional modules follow the `#` and include federation service, various monitoring components, workflow execution, and some older modules not generally installed.

For federated installations, you will need `federation-service`.

For production deployments, you will probably want to include  `federation-service`.

Authorization and authentication modules defined in  `CANDIG_AUTH_MODULES` are only installed if you run `make init-authx` during deployment.

## `make` Deployment

To deploy CanDIGv2, follow the docker deployment guide in `docs/`:

* [Docker Deployment Guide](./docs/install-docker.md)

There are other deprecated deployment guides in `docs`, but there are no guarantees that these still function:

* [Authentication and Authorization Deployment Guide](./docs/authx-setup.md)

View additional Makefile options with `make help`.

## Add new service

New services can be added under `lib` directory.  Please refer to the
[template for new services README](./lib/templates/README.md) for more details.
