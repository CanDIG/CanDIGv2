# Htsget Application

Htsget API implementation that is based on the [Htsget retrieval API specifications](http://samtools.github.io/hts-specs/htsget.html). Endpoints include /reads, /variants, and /data. Reads and variants are to request slices of URIs of a variant or read file, and /data is to return the file slices themselves. File storage and retrieval are implemented with two configurable options: a sqlalchemy compatible database, or DRS + MINIO. 

Thank you to [gel-htsget](https://github.com/genomicsengland/gel-htsget) for being a good starting point to this project

[![Build Status](https://travis-ci.org/CanDIG/htsget_app.svg?branch=master)](https://travis-ci.org/CanDIG/htsget_app)
[![CodeFactor](https://www.codefactor.io/repository/github/CanDIG/htsget_app/badge)](https://www.codefactor.io/repository/github/CanDIG/htsget_app)
[![PyUp](https://pyup.io/repos/github/CanDIG/htsget_app/shield.svg)](https://pyup.io/repos/github/CanDIG/htsget_app/)
[![Quay.io](https://quay.io/repository/candig/htsget_app/status)](https://quay.io/repository/candig/htsget_app)

## Stack
- [Connexion](https://github.com/zalando/connexion) for implementing the API
- [Sqlite3](https://www.sqlite.org/index.html)
- [ga4gh Data-Repostitory-Service(DRS)](https://github.com/ga4gh/data-repository-service-schemas)
- [minio-py](https://github.com/minio/minio-py)
- [Flask](http://flask.pocoo.org/)
- Python 3
- [Pysam](https://pysam.readthedocs.io/en/latest/api.html)
- Pytest
- Travis-CI

## Installation

The server software can be installed in a virtual environment:
```
python setup.py install
```

## Running

This application can be configured by way of the config.ini file in the root of the project.
The server can be run with: 

```
python htsget_server/server.py
```

A docker container can be pulled with
```
docker pull quay.io/candig/htsget_app
```

By default this application stores its files in a sqlite DB and on the current filesystem, but
it is also possible to use a DRS implementation to catalog these files and to host them in MinIO,
a S3-like self-hosted service. To do so, you can install [MinIO](https://min.io/) and 
[CHORD DRS](https://github.com/c3g/chord_drs). 

When these are setup, do please adjust the relevant variable in the config.ini file, namely:

```
FileRetrieval = minio
DRSPath = the url for the CHORD DRS installation
```

And of course, those in the "minio" section.

## Testing

For testing, a small test suite under tests/test_htsget_server.py can be run by starting the server and running:

```
pytest tests/test_htsget_server.py
```

If you are using DRS and MinIO for storing files, you may run this script (it'll upload the files
used in the aforementioned test suite in DRS):

```
python tests/upload_test_files_drs.py
pytest tests/test_htsget_server.py
```

For automated testing, activate the repo with [Travis-CI](https://travis-ci.com/getting_started)
