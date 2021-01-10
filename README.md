# CanDIG v2 PoC

- - -

## Overview

The CanDIG v2 project is a collection of heterogeneos services designed to work together to facilitate end to end
dataflow for genomic data.

```plaintext
                                                   +--------------+
                                                   | candig.local |
                                                   +-------+------+
                                                           |
                                               +-----------+-----------+
                                               | portainer:9010 (tcp)  |
                                               | portainer_agent       |
                                               +-----------+-----------+
                                                           |
                                                           |                 +----------------------------+
                                                +----------+---------+       | consul:8300      (tcp)     |
                  +-----------------------+     | traefik:8000 (tcp) |       |       :8400      (tcp)     |
                  | weave_app:4040  (tcp) +-----+        :80   (tcp) +-------+       :8500      (tcp)     |
                  | weave_probe           |     |        :443  (tcp) |       |       :8502      (tcp)     |
                  +-----------------------+     +----+-----+-----+---+       |       :8301-8302 (tcp/udp) |
                                                     |     |     |           |       :8600      (udp)     |
                                                     |     |     |           +----------------------------+
                                                     |     |     |
            +----------------monitoring--+           |     |     |           +-------------------logging--+
            | +-----------------------+  |           |     |     |           | +------------------------+ |
            | | prometheus:9090 (tcp) |  |           |     |     |           | | fluentd:24224 (tcp/udp)| |
            | +-----------------------+  |           |     |     |           | +------------------------+ |
            |                            +-----------+     |     +-----------+                            |
            | +------------------------+ |                 |                 |                            |
            | |node_exporter:9100 (tcp)| |                 |                 |                            |
            | +------------------------+ |                 |                 |                            |
            |                            |                 |                 | +------------------------+ |
            |   +-------------------+    |                 |                 | |elasticsearch:9200 (tcp)| |
            |   |cadvisor:9080 (tcp)|    |                 |                 | |             :9300 (tcp)| |
            |   +-------------------+    |                 |                 | +------------------------+ |
            |                            |                 |                 |                            |
            | +-----------------------+  |                 |                 |                            |
            | |alertmanager:9093 (tcp)|  |                 |                 |                            |
            | +-----------------------+  |                 |                 |                            |
            |                            |                 |                 |                            |
            |    +------------------+    |                 |                 |   +-------------------+    |
            |    |grafana:9888 (tcp)|    |                 |                 |   | kibana:5601 (tcp) |    |
            |    +------------------+    |                 |                 |   +-------------------+    |
            +----------------------------+                 |                 +----------------------------+
                                                           |
                                                           |
+---------------------------------+    +--------------------------------------+   +----------------------------+
|    +-----------------------+    |    | +----------------------------------+ |   | +------------------------+ |
|    | chord_metadata:8008   |    |    | | authorization_service:7000 (tcp) | |   | | cnv_service:8870 (tcp) | |
|    +-----------------------+    |    | +----------------------------------+ |   | +------------------------+ |
| +-----------------------------+ +----+  +-------------------------------+   +---+                            |
| | datasets_service:8880 (tcp) | |    |  | federation_service:4232 (tcp) |   |   |   +-------------------+    |
| +-----------------------------+ |    |  +-------------------------------+   |   |   | rnaget:3005 (tcp) |    |
+---------------------------------+    +--------------------------------------+   |   +-------------------+    |
                                                           |                      +----------------------------+
                                                  +--------+-----------+
                                                  | jupyter:8888 (tcp) |
                      +---------------------------+ rstudio:8787 (tcp) |         +--------------------------+
                      |                           +--------+-----------+         | candig_server:3001 (tcp) |
 +----------------------------------+                      |                     +--------------------------+
 | +------------------------------+ |          +---------------------------+
 | |  wes_server:5000  (tcp)      | |          | +-----------------------+ |      +-------------------+
 | |  toil_master:5050 (tcp)      | |          | | htsget_app:3333 (tcp) | +------+ igv_js:9091 (tcp) |
 | |  toil_ui:3000     (tcp)      | |          | +-----------------------+ |      +-------------------+
 | +------------------------------+ |          | +-----------------------+ |
 |                                  |          | | chord_drs:6000 (tcp)  | |
 | +------------------------------+ |          | +-----------------------+ |
 | |   toil_worker:5051 (tcp)     | |          +---------------------------+
 | +------------------------------+ |                       |
 +----------------------------------+              +--------+---------+
                                                   | minio:9000 (tcp) |
                                                   | minio_client     |
                                                   +------------------+

```

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
`${VAR}`.

```yaml
# example compose YAML using variable substitution with default option
services:
  consul:
    image: progrium/consul
    network_mode: ${DOCKER_MODE}
...
```

## `make` Deployment

To deploy CanDIGv2, follow one of the available install guides in `docs/`:

* [Docker Deployment Guide](./docs/install-docker.md)
* [Kubernetes Deployment Guide](./docs/install-kubernetes.md)
* [Tox Deployment Guide](./docs/install-tox.md)

View additional Makefile options with `make help`.


## Services and Components

The follwing table lists the details from the Data Flow Diagram in the "Overview" section.

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
