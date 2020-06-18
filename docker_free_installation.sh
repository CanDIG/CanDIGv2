git submodule update --init --recursive

# initialize conda environment
make init-conda

source miniconda3/etc/profile.d/conda.sh

conda activate candig

# download minio server/client
make bin-minio

# generate secrets for minio server/client
make minio-secrets

# start minio server instance
make minio-server

# start drs server instance
make conda-drs-server

# start htsget server instance
make conda-htsget-server

# start federation-service instance
make conda-federation-service
