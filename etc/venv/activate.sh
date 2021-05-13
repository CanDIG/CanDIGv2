source $PWD/bin/miniconda3/etc/profile.d/conda.sh
conda activate candig
export PATH="$PWD/bin:$PATH"
pip install -U -r $PWD/etc/venv/requirements.txt
#pip install -U -r $PWD/etc/venv/requirements-dev.txt
#eval $(docker-machine env manager)
