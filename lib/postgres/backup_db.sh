#!/usr/bin/env bash

python settings.py
source env.sh

db_name=$1

postgres=$(docker ps -a --format "{{.Names}}" | grep postgres-db | awk '{print $1}')
PGDATA=$(docker exec $postgres sh -c 'echo $PGDATA')

echo "Making backup of ${db_name} database..."
docker exec $postgres sh -c "pg_dump -U admin -d ${db_name} -f ${PGDATA}/${db_name}-backup.sql"
if [[ $? -eq 0 ]]; then
    docker cp $postgres:$PGDATA/${db_name}-backup.sql $(pwd)/$BACKUP_LOCATION/${db_name}-backup.sql
fi
docker exec $postgres sh -c "rm ${PGDATA}/${db_name}-backup.sql"

echo
echo "Saved $db_name backup to $BACKUP_LOCATION"
ls -l $(pwd)/$BACKUP_LOCATION/${db_name}-backup.sql
