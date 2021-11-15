#!/usr/bin/env bash

LOGFILE=$PWD/candig/tmp/progress.txt

grep -q "finished provision.sh" $LOGFILE
if [ $? -ne 0 ]; then
  echo "ERROR! Provisioning failed, do not set up containers" | tee -a $LOGFILE
  exit 1
fi
echo "started setup_containers.sh" | tee -a $LOGFILE
cd $1
source $PWD/bin/miniconda3/etc/profile.d/conda.sh
conda activate candig
export PATH="$PWD/bin:$PATH"
eval $(docker-machine env manager)

echo "  started make init-docker" | tee -a $LOGFILE
make init-docker
if [ $? -ne 0 ]; then
  echo "ERROR! make init-docker failed" | tee -a $LOGFILE
  exit 1
fi

echo "  started make docker-pull" | tee -a $LOGFILE
make docker-pull
if [ $? -ne 0 ]; then
  echo "ERROR! make docker-pull failed" | tee -a $LOGFILE
  exit 1
fi

echo "  started make compose" | tee -a $LOGFILE
make compose
if [ $? -ne 0 ]; then
  echo "ERROR! make compose failed" | tee -a $LOGFILE
  exit 1
fi

echo "finished setup_containers.sh" | tee -a $LOGFILE
