# CanDIG v2

- - -

## Overview

The CanDIG v2 project is a collection of heterogeneous services designed to work together to facilitate end to end
dataflow for genomic data.

## Installation

CanDIG uses a make-based deployment process, with services containerized in Docker. To deploy CanDIGv2, follow the installation guides in `docs/`:

* [CanDIG Deployment Guide](./docs/install-candig.md)

See [Interact with the stack](docs/interact-with-the-stack.md) for a guide to additional options or view all Makefile options with `make help`.

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
 |    ├── tests/                   - integration and performance tests (under development)
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
| CanDIGv2 Ingest Service     | [`candigv2-ingest`](https://github.com/CanDIG/candigv2-ingest)        | Ingests clinical and genomic data into the CanDIG infrastructure. |
| Clinical ETL Code         | [`clinical_ETL_code`](https://github.com/CanDIG/clinical_ETL_code)    | Code to convert spreadsheet format into the MoH data model in preparation for ingest into `katsu` |
| Federation Service        | [`federation-service`](https://github.com/CanDIG/federation_service)  | Distributes requests across each federated node of the distributed infrastructure   |
| HTSGet                    | [`htsget_app`](https://github.com/CanDIG/htsget_app)                  | Implementation of GA4GH htsget API which ingests and indexes VCF files and stores GA4GH DRS objects for retrieval |
| Katsu                     | [`katsu`](https://github.com/CanDIG/katsu)                            | Manages the clinical metadata in a PostgreSQL database |
| CanDIG OPA                | [`candig-opa`](https://github.com/CanDIG/candig-opa)                  | Manages role-based access policies   |
| Query service             | [`candigv2-query`](https://github.com/CanDIG/candigv2-query)                   | Manages front-end querying of services |

As well as in-house developed services, the CanDIG stack relies on external software which is configured to work within the stack, configurations are found in the [`/lib`](/lib) folder for each software, these include:

| Service/Component Name                  | Role                                 |
|-----------------------------------------|--------------------------------------|
| [Keycloak](https://www.keycloak.org/)   | Authentication management            |
| [minio](https://min.io/)                | Object storage for genomic files     |
| [OPA](https://www.openpolicyagent.org/) | Manages role-based access policies   |
| [Tyk](https://tyk.io/)                  | API management and redirection       |
| [Vault](https://www.vaultproject.io/)   | Secret and password management       |

## Adding a new service

New services can be added under `lib` directory.  Please refer to the
[template for new services README](./lib/templates/README.md) for more details.
