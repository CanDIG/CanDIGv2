#!/usr/bin/env bash

set -x

cd /notebooks/demo

git clone https://github.com/ericmjl/bayesian-stats-modelling-tutorial

pushd bayesian-stats-modelling-tutorial
conda env create --clone base -f environment.yml
source activate bayesian-modelling-tutorial
python -m ipykernel install --user --name bayesian-modelling-tutorial
source deactivate
popd

git clone https://github.com/amueller/scipy-2018-sklearn.git

pushd scipy-2018-sklearn
conda env create --clone base -f environment.yml
source activate tutorial-sklearn
python -m ipykernel install --user --name tutorial-sklean
source deactivate
popd

git clone https://github.com/dask/dask-examples.git

pushd dask-examples
conda env create --clone base -n dask-kernel -f binder/environment.yml
source activate dask-kernel
python -m ipykernel install --user --name dask-kernel
source deactivate
popd

git clone https://github.com/mrocklin/pydata-nyc-2018-tutorial.git

pushd pydata-nyc-2018-tutorial
conda env create --clone base -f binder/environment.yml
python -m ipykernel install --user --name pangeo
source deactivate
popd

git clone https://github.com/eriknw/dask-patternsearch.git

pushd dask-patternsearch
conda env create --clone base -n dask-patternsearch python=3 dask distributed
source activate dask-patternsearch
pip install git+https://github.com/dask/dask.git --upgrade
pip install git+https://github.com/dask/distributed.git --upgrade
pip install git+https://github.com/eriknw/dask-patternsearch.git --upgrade
python -m ipykernel install --user --name dask-patternsearch
source deactivate
popd

git clone https://github.com/MaayanLab/biojupies.git

pushd biojupies
conda env create --clone base -n biojupies
source activate biojupies
Rscript docker/requirements.R
pip3 install -r docker/requirements.txt
pip3 install multiprocess
python docker/download-libraries.py
python -m ipykernel install --user --name biojupies
source deactivate
popd

git clone https://github.com/CanDIG/CanDIGv2

pushd CanDIGv2
conda env create --clone base -f etc/conda/environment.yml
source activate candig
python -m ipykernel install --user --name candig
source deactivate
popd

git clone https://github.com/ipython/ipython-in-depth.git

pushd ipython-in-depth
conda env create --clone base -n ipython-in-depth -f binder/environment.yml
source activate ipython-in-depth
python -m ipykernel install --user --name ipython-in-depth
source deactivate
popd

git clone git@github.com:CanDIG/ga4gh_readthrough_fusions_example.git
