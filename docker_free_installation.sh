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
# start drs server instance
# start htsget server instance
# start federation service
make minio-server & make conda-drs-server & make conda-htsget-server & make conda-federation-service
