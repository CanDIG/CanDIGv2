# This script simply facilitates the running of this test module via the project Makefile

# For further reading, see :
# https://docs.pytest.org/en/latest/contents.html

export PYTHONPATH=./src;
export DRIVER_ENV=$2
export HEADLESS_MODE=$3

pytest --rootdir=$(pwd)/etc/tests/integration/authx -s -v -n=$1 --ignore=lib/ --ignore=bin/ --ignore=docs/ --ignore=tmp/ 
