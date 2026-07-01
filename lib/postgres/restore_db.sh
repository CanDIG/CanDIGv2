#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

db_name=$1
module=$2

postgres=$(docker ps --format "{{.Names}}" | grep postgres-db | awk '{print $1}')
container=$(docker ps --format "{{.Names}}" | grep ${module}_1 | awk '{print $1}')

# look for database backup to restore
restore=$(cat lib/$module/restore.txt)
if [[ $? -eq 0 ]]; then
    ls $restore
    if [[ $? -eq 0 ]]; then
        echo "restoring from backup file" $restore
        docker stop $container
        docker cp $restore $postgres:/var/lib/postgresql/data/${module}_restore.sql
        docker exec $postgres sh -c "dropdb -U admin $db_name"
        docker exec $postgres sh -c "createdb -U admin $db_name"
        docker exec $postgres sh -c "psql -U admin -d $db_name < /var/lib/postgresql/data/${module}_restore.sql"
        docker exec $postgres sh -c "rm /var/lib/postgresql/data/${module}_restore.sql"
        mv lib/$module/restore.txt lib/$module/restored.txt
        docker start $container
    fi
fi
