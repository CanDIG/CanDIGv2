source $PWD/bin/miniconda3/etc/profile.d/conda.sh
conda activate candig
pip install -U -r $PWD/etc/venv/requirements.txt
#pip install -U -r $PWD/etc/venv/requirements-dev.txt
export PATH="$PWD/bin:$PATH"
#eval $(docker-machine env manager)
