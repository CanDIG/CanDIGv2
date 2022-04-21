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

echo "  started make init-authx " | tee -a $LOGFILE
make init-authx
if [ $? -ne 0 ]; then
  echo "ERROR! make init-authx failed" | tee -a $LOGFILE
  exit 1
fi

echo "finished setup_auth.sh" | tee -a $LOGFILE
