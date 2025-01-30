#!/usr/bin/env bash

set -Euo pipefail

export PGPASSWORD=$(< /run/secrets/db_password)

# check if the database exists
check_db_exist() {
    psql --quiet -h "$DB_HOST" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"
}

# create database
create_db() {
    echo "Initializing database..."
    createdb -h "$DB_HOST" -U "$DB_USER" "$DB_NAME"
    echo "Database created successfully."
}

# Wait for postgres container to be ready
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Waiting for the database to be ready..."
  sleep 1
done

# Postgres container connected, check to create or skip tds db
if check_db_exist; then
    echo "Database already exists. Skipping the database creation."
else
    create_db
fi