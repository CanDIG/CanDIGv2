#!/bin/bash
set -e

# --- Configuration ---
CONTAINER_NAME_PATTERN="postgres-db"
DB_USER="admin"
DB_NAME="omop"
CDM_SCHEMA="public"

# --- SQL Files ---
DDL_FILE="ddl/ddl.sql"
PK_FILE="ddl/primary_keys.sql"
FK_FILE="ddl/constraints.sql"
INDICES_FILE="ddl/indices.sql"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/../.." && pwd)
PASSWORD_FILE="${PROJECT_ROOT}/tmp/postgres/db-secret"

echo
echo "--- Starting OMOP Database Setup ---"

echo "Step 1: Get database password"
if [ ! -f "${PASSWORD_FILE}" ]; then
  echo "Error: Password file not found at '${PASSWORD_FILE}'"
  exit 1
fi

export PGPASSWORD=$(cat "${PASSWORD_FILE}")
echo "---"

echo "Step 2: Find db container by name"
OMOP_CONTAINER_NAME=$(docker ps --filter "name=${CONTAINER_NAME_PATTERN}" --format "{{.Names}}")

if [ -z "${OMOP_CONTAINER_NAME}" ]; then
  echo "Error: No running container found with a name matching '${CONTAINER_NAME_PATTERN}'."
  exit 1
fi

# Wait for db container to be ready
echo "Waiting for db to be ready..."
until docker exec "${OMOP_CONTAINER_NAME}" pg_isready -h localhost -p 5432 -U "${DB_USER}"; do
  echo "Waiting for the database to be ready..."
  sleep 1
done
echo "PostgreSQL is ready."
echo "---"

# Check if the database already exists. If yes, stop.
echo "Step 3: Checking if database '${DB_NAME}' already exists..."

if docker exec "${OMOP_CONTAINER_NAME}" psql -U "${DB_USER}" -lqt | cut -d \| -f 1 | grep -qw "${DB_NAME}"; then
    echo "Database '${DB_NAME}' already exists. Skipping setup."
    unset PGPASSWORD
    exit 0
else
    echo "Database '${DB_NAME}' not found. Proceeding with creation..."
    docker exec "${OMOP_CONTAINER_NAME}" createdb -U "${DB_USER}" "${DB_NAME}"
    echo "Database '${DB_NAME}' created successfully."
fi

TEMP_DIR=$(mktemp -d)

run_sql_file() {
  local description=$1
  local input_file=$2
  local processed_file="${TEMP_DIR}/$(basename "$input_file")"
  local full_input_path="${SCRIPT_DIR}/${input_file}"

  if [ ! -f "$full_input_path" ]; then
    echo "Error: Source file '${full_input_path}' not found."
    rm -rf "${TEMP_DIR}"
    exit 1
  fi

  sed "s/@cdmDatabaseSchema\./${CDM_SCHEMA}\./g" "$full_input_path" > "$processed_file"

  cat "$processed_file" | docker exec -i "${OMOP_CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}" --quiet

  echo "Successfully ${description}."
}

run_sql_file "Creating Tables (DDL)" "$DDL_FILE"
run_sql_file "Adding Primary Keys" "$PK_FILE"
run_sql_file "Adding Foreign Key Constraints" "$FK_FILE"
run_sql_file "Creating Indices" "$INDICES_FILE"

# Clean up
rm -rf "${TEMP_DIR}"
echo "Cleaned up temporary files."

echo "--- OMOP Setup Complete! ---"
echo "Database '${DB_NAME}' is ready on container '${OMOP_CONTAINER_NAME}'."

unset PGPASSWORD