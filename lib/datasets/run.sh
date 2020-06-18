set -e

source .env

[ -z $CONDA_DEFAULT_ENV ] && \
  source $(pwd)/bin/miniconda3/etc/profile.d/conda.sh && \
  conda activate ${VENV_NAME}

pushd $(pwd)/lib/datasets/datasets_service/
  pip install -r requirements.txt
  python -m candig_dataset_service --host ${DATASETS_SERVICE_HOST} --port ${DATASETS_SERVICE_PORT}
popd
