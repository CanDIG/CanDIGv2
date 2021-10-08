# Katsu Metadata Service

![Build Status](https://travis-ci.com/bento-platform/katsu.svg?branch=master)
[![codecov](https://codecov.io/gh/bento-platform/katsu/branch/master/graph/badge.svg)](https://codecov.io/gh/bento-platform/katsu)

## Table of Contents

  * [License](#license)
  * [Funding](#funding)
  * [Architecture](#architecture)
  * [REST API Highlights](#rest-api-highlights)
  * [Install](#install)
  * [Authentication](#authentication)
     * [Note on Permissions](#note-on-permissions)
     * [Authorization inside CanDIG](#authorization-inside-candig)
  * [Developing](#developing)
     * [Branching](#branching)
     * [Tests](#tests)
     * [Terminal Commands](#terminal-commands)
        * [Bento Commands](#bento-commands)
        * [Patient Commands](#patient-commands)
        * [Phenopacket Commands](#phenopacket-commands)
     * [Accessing the Django Shell from inside a Bento Container](#accessing-the-django-shell-from-inside-a-bento-container)

## License

The majority of the Katsu Metadata Service is licensed under the LGPLv3 license; copyright (c) 2019-2020 the Canadian
Centre for Computational Genomics.

Portions are copyright (c) 2019 Julius OB Jacobsen, Peter N Robinson, Christopher J Mungall (Phenopackets); licensed
under the BSD 3-clause license.

## Funding

Katsu Metadata service development is funded by CANARIE under the CHORD project.

## Architecture

Katsu Metadata Service is a service to store epigenomic metadata.

1. Patients service handles anonymized individual’s data (individual id, sex, age or date of birth)
    * Data model: aggregated profile from GA4GH Phenopackets Individual, FHIR Patient and mCODE Patient.

2. Phenopackets service handles phenotypic and clinical data
    * Data model: [GA4GH Phenopackets schema](https://github.com/phenopackets/phenopacket-schema)

3. mCode service handles patient's oncology related data.
    * Data model: [mCODE data elements](https://mcodeinitiative.org/)

4. Experiments service handles experiment related data.
    * Data model: derived from [IHEC Metadata Experiment](https://github.com/IHEC/ihec-ecosystems/blob/master/docs/metadata/2.0/Ihec_metadata_specification.md#experiments)

5. Resources service handles metadata about ontologies used for data annotation.
    * Data model: derived from Phenopackets Resource profile

6. CHORD service  handles metadata about dataset, has relation to phenopackets (one dataset can have many phenopackets)
    * Data model: [DATS](https://github.com/datatagsuite)  + [GA4GH DUO](https://github.com/EBISPOT/DUO)

7. Rest api service handles all generic functionality shared among other services


## REST API highlights

* Standard api delivers data in snake_case.
To retrieved data in json compliant with phenopackets that uses camelCase append `?format=phenopackets` .

* Data can be ingested and retrieved in snake_case or camelCase.

* Other available renderers:
Phenopackets model is mapped to [FHIR](https://www.hl7.org/fhir/) using
[Phenopackets on FHIR](https://aehrc.github.io/fhir-phenopackets-ig/) implementation guide.
To retrieve data in fhir append `?format=fhir` .

* Ingest endpoint: `/private/ingest`.


## Install

Install the git submodule for DATS JSON schemas (if you did not clone recursively):

```
git submodule update --init
```

The service uses PostgreSQL database for data storage.

* Create and activate virtual environment
* Run: `pip install -r requirements.txt`
* To configure the application (such as the DB credentials) we are using python-dotenv:
    - Take a look at the .env-sample file at the root of the project
    - You can export these in your virtualenv or simply `cp .env-sample .env`
    - python-dotenv can handle either (a local .env will override env vars though)


* Run:

```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

* Development server runs at `localhost:8000`


## Authentication

Default authentication can be set globally in `settings.py`

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
    	'rest_framework.authentication.BasicAuthentication',
    	'rest_framework.authentication.SessionAuthentication',
    ]
}
# ...
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
```

By default, the service ships with a custom remote user middleware and backend
compatible with the CHORD project. This middleware isn't particularly useful
for a standalone instance of this server, so it can be swapped out.

### Note on Permissions

By default, `katsu` uses the CHORD permission system, which
functions as follows:

  * URLs under the `/private` namespace are assumed to be protected by an
    **out-of-band** mechanism such as a properly-configured reverse proxy.
  * Requests with the headers `X-User` and `X-User-Role` can be authenticated
    via a Django Remote User-type system, with `X-User-Role: owner` giving
    access to restricted endpoints and `X-User-Role: user` giving less trusted,
    but authenticated, access.

This can be turned off with the `CHORD_PERMISSIONS` environment variable and/or
Django setting, or with the `AUTH_OVERRIDE` Django setting.

### Authorization inside CanDIG

When ran inside the CanDIG context, to properly implement authorization you'll
have to do the following:

1. Make sure the CHORD_PERMISSIONS is set to "false"
2. Set INSIDE_CANDIG to "true"
3. Provide the URL for the OPA instance in CANDIG_OPA_URL


## Developing

### Branching

All new feature requests and non-critical bug fixes should be merged into the
`develop` branch. `develop` is treated as a "nightly" version. Releases are
created from `develop`-to-`master` merges; patch-release work can be branched
out and tagged from the tagged major/minor release in `master`.

### Tests

Tests are located in tests directory in an individual app folder.

Run all tests and linting checks for the whole project:

```bash
tox
```

Run all tests for the whole project:

```bash
python manage.py test
```

Run tests for an individual app, e.g.:

```bash
python manage.py test chord_metadata_service.phenopackets.tests.test_api
```

Test and create `coverage` HTML report:

```bash
tox
coverage html
```

### Terminal Commands

Katsu ships with a variety of command-line helpers to facilitate common actions
that one might perform. 

To run them, the Django `manage.py` script is used.

#### Project/Dataset/Table/Ingestion Commands

```
$ ./manage.py create_project "project title" "project description"
Project created: test (ID: 756a4530-59b7-4d47-a04a-c6ee5aa52565)
```

Creates a new project with the specified title and description text. Returns
output including the new ID for the project, which is needed when creating
datasets under the project.

```
$ ./manage.py create_dataset \
  "dataset title" \
  "dataset description" \
  "David Lougheed <david.lougheed@example.org>" \
  "756a4530-59b7-4d47-a04a-c6ee5aa52565"  \
  ./examples/data_use.json
Dataset created: dataset title (ID: 2a8f8e68-a34f-4d31-952a-22f362ebee9e)
```

* `David Lougheed <david.lougheed@example.org>`: Dataset use contact information
* `756a4530-59b7-4d47-a04a-c6ee5aa52565`: Project ID to put the dataset under
* `./examples/data_use.json`: Path to data use JSON

Creates a new dataset under the project specified (with its ID), with 
corresponding title, description, contact information, and data use conditions.

```
$ ./manage.py create_table \
  "table name" \
  phenopacket \
  "2a8f8e68-a34f-4d31-952a-22f362ebee9e"
Table ownership created: dataset title (ID: 2a8f8e68-a34f-4d31-952a-22f362ebee9e) -> 0d63bafe-5d76-46be-82e6-3a07994bac2e
Table created: table name (ID: 0d63bafe-5d76-46be-82e6-3a07994bac2e, Type: phenopacket)
```

* `table name`: Name of the new table created
* `phenopacket`: Table data type (either `phenopacket` or `experiment`)
* `2a8f8e68-a34f-4d31-952a-22f362ebee9e`: Dataset ID to put the table under

Creates a new data table under the dataset specified (with its ID), with a 
corresponding name and data type (either `phenopacket` or `experiment`.)

```"
$ ./manage.py ingest \
  "0d63bafe-5d76-46be-82e6-3a07994bac2e" \
  ./examples/1000g_phenopackets_1_of_3.json
...
Ingested data successfully.
```

* `0d63bafe-5d76-46be-82e6-3a07994bac2e`: ID of table to ingest into
* `./examples/1000g_phenopackets_1_of_3.json`: Data to ingest (in the format 
  accepted by the Phenopackets workflow or the Experiments workflow, depending
  on the data type of the table)
  
#### Patient Commands

```
$ ./manage.py patients_build_index
...
```

Builds an ElasticSearch index for patients in the database.
  
#### Phenopacket Commands

```
$ ./manage.py phenopackets_build_index
...
```

Builds an ElasticSearch index for Phenopackets in the database.

### Accessing the Django Shell from inside a Bento Container

Assuming `chord_singularity` is being used, the following commands can be used
to bootstrap your way to a `katsu` environment within a Bento
container:

```bash
./dev_utils.py --node x shell
source /chord/services/metadata/env/bin/activate
source /chord/data/metadata/.environment
export $(cut -d= -f1 /chord/data/metadata/.environment)
DJANGO_SETTINGS_MODULE=chord_metadata_service.metadata.settings django-admin shell
```

From there, you can import models and query the database from the REPL.
