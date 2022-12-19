#!/usr/bin/env bash

set -euo pipefail

PYTHON_BIN_PATH="$(python3 -m site --user-base)/bin"
export PATH="$PATH:$PYTHON_BIN_PATH"
pipenv shell
