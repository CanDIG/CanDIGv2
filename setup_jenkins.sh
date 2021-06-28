#!/usr/bin/env bash


cp etc/env/example.env .env

tail -n 2 $WORKING_DIR/progress.txt | grep -q "finished init-conda"; if [ $? -eq 0 ]; then echo "hi"; fi

make bin-all
make init-conda
. $PWD/bin/miniconda3/etc/profile.d/conda.sh
conda activate candig
pip install -U -r $PWD/etc/venv/requirements.txt

cat $WORKING_DIR/progress.txt
