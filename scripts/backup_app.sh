#!/bin/bash

# Get the optional argument for the dump filename
DUMP_NAME=$1

# If no argument is provided, use the default name
if [ -z "$DUMP_NAME" ]; then
    DUMP_NAME="dump_$(date +"%Y-%m-%d_%H_%M_%S").gz"
else
    DUMP_NAME="${DUMP_NAME}_$(date +"%Y-%m-%d_%H_%M_%S").gz"
fi

# Get the container ID of the running PostgreSQL image
POSTGRES_DOCKER_ID=$(docker ps | grep "postgres" | awk '{print $1}')

# Check if the container ID was found
if [ -z "$POSTGRES_DOCKER_ID" ]; then
    echo "Error: PostgreSQL container not found!"
    exit 1
fi

# Run the backup command for the 'app' database
docker exec -t $POSTGRES_DOCKER_ID pg_dump -c -U postgres app | gzip > "./db-backups/$DUMP_NAME"

echo "Backup completed successfully!"
exit 0
