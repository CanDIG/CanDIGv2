#!/usr/bin/env bash

set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
	source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
	conda activate ${VENV_NAME}

# add any exports here
# remember that secrets should be passed as opaque file tokens
#example:
#export SERVICE_PORT=${SERVICE_PORT_FROM_ENV_FILE}
#export SERVICE_SECRET=$(pwd)/{{path_to_secret}}
#bad example:
#export SERVICE_SECRET='plaintext_secret'

pushd $(pwd)/lib/{{service_name}}/chord_drs
# use submodule name if needed
pushd $(pwd)/lib/{{service_name}}/chord_drs
#pushd $(pwd)/lib/{{service_name}}/{{submodule_name}}
	# add the steps necessary to run service in virtualenv
	# example:
	#pip install -r requirements.txt
	#flask db upgrade
	#flask run --host 0.0.0.0 --port ${{{service_port}}}
#popd
