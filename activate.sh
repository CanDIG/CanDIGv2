#!/usr/bin/env bash

set -euo pipefail

PYTHON_BIN_PATH="$(python3 -m site --user-base)/bin"
export PATH="$PATH:$PYTHON_BIN_PATH"

pip3 install pipenv || echo 'pipenv is already installed...'

which pipenv || echo "cannot find pipenv in PATH $PATH"

pipenv --python 3.10 || echo 'pipenv is already created...'
pipenv install --requirements requirements.txt || echo 'requirements.txt already installed...'
pipenv shell
