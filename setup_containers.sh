#!/usr/bin/env bash

source $PWD/bin/miniconda3/etc/profile.d/conda.sh
conda activate candig
export PATH="$PWD/bin:$PATH"
eval $(docker-machine env manager)
make init-docker
make images
