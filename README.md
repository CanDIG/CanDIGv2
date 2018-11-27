# CanDIG v2 PoC
- - -

## Overview

The CanDIG v2 project is a collection of heterogeneos services designed to work together to facilitate end to end
dataflow for genomic data.

## Project Structure

```bash

├── .env - docker-compose and Makefile global variables
├── lib - contains modules of servies/apps
│   ├── ga4gh-dos - example service, make compose-ga4gh-dos
│   │   ├── demo.py
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile
│   │   └── gdc_dos.py
├── Makefile - actions for repeatable testing/deployment

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
## `make` Deployment

```bash

# view available options
make

# initialize docker swarm and create required docker networks
make init

# deploy/test all modules in lib/ using docker-compose
make compose

# deploy/test all modules in lib/ using docker stack
make stack

# (re)build service image and deploy/test using docker-compose
# $module is the name of the sub-folder in lib/
module=htsget-server
make build-${module}

# deploy/test individual modules using docker-compose
# $module is the name of the sub-folder in lib/
module=ga4gh-dos
make compose-${module}

# deploy/test indivudual modules using docker stack
# $module is the name of the sub-folder in lib/
module=igv-js
make stack-${module}

# cleanup environment
make clean

```

## `mc` Client Examples

```bash

# Example - Minio Cloud Storage
mc config host add minio http://192.168.1.51 BKIKJAA5BMMU2RHO6IBB V7f1CwQqAcwo80UEIJEjc5gVQUSSx5ohQ9GSrr12

# Example - Amazon S3 Cloud Storage
mc config host add s3 https://s3.amazonaws.com BKIKJAA5BMMU2RHO6IBB V7f1CwQqAcwo80UEIJEjc5gVQUSSx5ohQ9GSrr12

```

## Data Repository Service Schemas

```bash

wget http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz

md5sum chr22.fa.gz

# 41b47ce1cc21b558409c19b892e1c0d1  chr22.fa.gz

curl -X POST -H 'Content-Type: application/json' \
  --data '{"data_object":
          {"id": "hg38-chr22",
           "name": "Human Reference Chromosome 22",
           "checksums": [{"checksum": "41b47ce1cc21b558409c19b892e1c0d1", "type": "md5"}],
           "urls": [{"url": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz"}],
           "size": "12255678"}}' http://localhost:8080/ga4gh/dos/v1/dataobjects

# We can then get the newly created Data Object by id
curl http://localhost:8080/ga4gh/dos/v1/dataobjects/hg38-chr22

# Or by checksum!
curl -X GET http://localhost:8080/ga4gh/dos/v1/dataobjects -d checksum=41b47ce1cc21b558409c19b892e1c0d1

```
## References

* [1][Minio Client Quickstart](https://docs.minio.io/docs/minio-client-quickstart-guide#add-a-cloud-storage-service)
* [2][GA4GH DRS Schemas](https://github.com/ga4gh/data-repository-service-schemas)
* [3][GA4GH DOS Server Quickstart](https://data-object-service.readthedocs.io/en/latest/quickstart.html)
