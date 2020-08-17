# CanDIG Install Guide

- - -

## Install Dependencies

Since Tox is a Python package it is recommended to install it on a Python virtual environment using:

```bash
pip install tox
```

Also python-dotenv should be installed on your virtual environment using:

```bash
pip install python-dotenv
```

## Install CanDIG Dependencies

1. Clone/pull latest CanDIGv2 repo from `https://github.com/CanDIG/CanDIGv2.git`

2. Create/modify `.env` file
```bash
# Copy and Edit `.env` with your site's local configuration
`cp -i etc/env/example.env .env`
```

3. Initialize submodules
```bash
git submodule update --init --recursive
```

4. Create CanDIG Daemons

```bash
# view helpful commands
make

# run candig services in screen terminals
make tox

# to run an individual service
make tox-service_name_here
```

## Add services to tox.ini file

In order to add and run a new service, you must follow bellow steps:

1. Add service as a submodule (Please note, if the service is from Pypi website, you may skip this step)

```bash
git submodule add http://github.com/username/service_name libs/service_name_dir
```

2. Add service to ```tox.ini``` file using bellow sections:

```ini
[testenv:new_service_name]
changedir = {toxinidir}/lib/service_name_dir/github_dir_name
; Set 'deps' only if the service has a requirement file
deps=-r{toxinidir}/lib/service_name_dir/github_dir_name/requirements.txt

commands=
    ; Under commands you may add the commands to install the service, bellow some examples.
    python setup.py install
    pip install service_name
    ; And also commands to run the service, below some examples.
    ; Note that your machine should have 'screen' installed
    screen -dmS {envname} ./manage.py runserver {env:IP_FROM_ENV_FILE}:{env:PORT_FROM_ENV_FILE}
    screen -dmS {envname} flask run --host {env:IP_FROM_ENV_FILE} --port {env:PORT_FROM_ENV_FILE}

; If you need to execute, for instance, a Unix command, that should be added under 'whitelist_externals' section following below sample:
whitelist_externals=
    mkdir

; If the service requires a specific version of Python (let's say Python3.5) you may use 'basepython' section:
; Note that your machine must have Python 3.5 installed in order to execute this operation
basepython=python3.5
```
