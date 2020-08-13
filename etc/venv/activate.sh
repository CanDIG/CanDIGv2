source ./bin/miniconda3/etc/profile.d/conda.sh
conda activate candig
pip install -r ./etc/venv/requirements.txt
export PATH="$PWD/bin:$PATH"
eval $(bin/docker-machine env manager)
