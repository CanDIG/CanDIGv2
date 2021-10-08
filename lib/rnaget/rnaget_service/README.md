# rnaget Microservice
[![Build Status](https://travis-ci.org/CanDIG/rnaget_service.svg?branch=master)](https://travis-ci.org/CanDIG/rnaget_service)
[![Code Coverage](https://img.shields.io/codecov/c/github/CanDIG/rnaget_service/master.svg)](https://codecov.io/gh/CanDIG/rnaget_service)


Based on CanDIG demo projects: [OpenAPI variant service demo](https://github.com/ljdursi/openapi_calls_example), [Python Model Service](https://github.com/CanDIG/python_model_service). This is a Proof-of-Concept implementation of the [GA4GH rnaget API](https://github.com/ga4gh-rnaseq/schema), used to query and download RNA quantification matrix data.

## Schema info
For more information about the schemas used visit https://github.com/ga4gh-rnaseq/schema

## Stack

- [Connexion](https://github.com/zalando/connexion) for implementing the API
- [SQLAlchemy](http://sqlalchemy.org), using [Sqlite3](https://www.sqlite.org/index.html) for ORM
- [Bravado-core](https://github.com/Yelp/bravado-core) for Python classes from the spec
- [Dredd](https://dredd.readthedocs.io/en/latest/) and [Dredd-Hooks-Python](https://github.com/apiaryio/dredd-hooks-python) for testing
- [HDF5](https://www.hdfgroup.org/solutions/hdf5/) for matrix store & operations
- Python 3
- Pytest, tox
- Travis-CI

## Installation

The server software can be installed in a py3.6+ virtual environment:

```
pip install -r requirements.txt
pip install -r requirements_dev.txt
python setup.py develop
```

for automated testing you can install dredd; assuming you already have node and npm installed,

```
npm install -g dredd
```

### Running

Once running, a Swagger UI can be accessed at: `/rnaget/ui`

To specify your own database & log output, the server can be started with:

```
candig_rnaget --host=0.0.0.0 --port=3005 --database=data/test.db --logfile=/path/to/logs --loglevel=WARN
```

For testing, the dredd config is currently set up to launch the service itself, so no server needs be running:

```
cd tests
dredd --hookfiles=dreddhooks.py
```
