#!/usr/bin/env bash

set -xe

mesos-master --registry=in_memory --ip=0.0.0.0 --port=5050 --allocation_interval=500ms &

wes-server $*
