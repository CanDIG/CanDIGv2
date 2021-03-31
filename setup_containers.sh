#!/usr/bin/env bash
echo "started setup_containers.sh" | tee -a ~/progress.txt
cd $1
source $PWD/bin/miniconda3/etc/profile.d/conda.sh
conda activate candig
export PATH="$PWD/bin:$PATH"
eval $(docker-machine env manager)
make init-docker
make images
make compose
echo "finished setup_containers.sh" | tee -a ~/progress.txt
