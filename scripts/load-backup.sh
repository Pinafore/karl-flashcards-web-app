#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1"
    exit 1
}

# Check the number of arguments provided
if [ "$#" -lt 1 ]; then
    handle_error "No arguments provided. Usage: $0 <backup_file_path> [path_to_.env_file]"
elif [ "$#" -gt 2 ]; then
    handle_error "Too many arguments provided. Usage: $0 <backup_file_path> [path_to_.env_file]"
fi

BACKUP_FILE=$1

# Check if the .env file argument is provided, if not default to .env in the current directory
if [ -z "$2" ]; then
    ENV_FILE="./.env"
else
    ENV_FILE=$2
fi


# Extract POSTGRES_PASSWORD from the .env file
POSTGRES_PASSWORD=$(grep POSTGRES_PASSWORD $ENV_FILE | cut -d '=' -f2)

# Run the backup.sh script first
./scripts/backup.sh
if [ $? -ne 0 ]; then
    handle_error "Backup failed. Aborting restore."
fi

# Extract the base name without the .gz extension for the cat command later
BASE_NAME=$(basename $BACKUP_FILE .gz)
DIR_NAME=$(dirname $BACKUP_FILE)
FULL_PATH="$DIR_NAME/$BASE_NAME"

# Unzip the backup file
gunzip -c $BACKUP_FILE > $BASE_NAME
if [ $? -ne 0 ]; then
    handle_error "Failed to unzip the backup file. Aborting restore."
fi

# Get the container ID of the running PostgreSQL image
POSTGRES_DOCKER_ID=$(docker ps | grep "postgres" | awk '{print $1}')

# Check if the container ID was found
if [ -z "$POSTGRES_DOCKER_ID" ]; then
    handle_error "PostgreSQL container not found! Aborting restore."
fi

# Execute commands inside the PostgreSQL container
docker exec -ti $POSTGRES_DOCKER_ID bash -c "
    psql -h localhost postgres postgres -c \"UPDATE pg_database SET datallowconn = 'false' WHERE datname = 'app';\"
    psql -h localhost postgres postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'app';\"
    psql -h localhost postgres postgres -c \"DROP DATABASE app;\"
"

if [ $? -ne 0 ]; then
    handle_error "Failed to execute SQL commands inside the container. Aborting restore."
fi

# Load the backup into the PostgreSQL container
cat $FULL_PATH | docker exec -i $POSTGRES_DOCKER_ID psql -U postgres
if [ $? -ne 0 ]; then
    handle_error "Failed to load the backup into the PostgreSQL container."
fi

# Reset the postgres user's password using the extracted POSTGRES_PASSWORD
docker exec -it $POSTGRES_DOCKER_ID bash -c "psql -U postgres <<EOF
ALTER USER postgres WITH PASSWORD '$POSTGRES_PASSWORD';
EOF"
if [ $? -ne 0 ]; then
    handle_error "Failed to reset the postgres user's password."
fi




echo "Backup loaded successfully!"
