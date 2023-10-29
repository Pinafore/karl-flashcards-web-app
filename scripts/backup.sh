#!/bin/bash

# Get the container ID of the running PostgreSQL image
POSTGRES_DOCKER_ID=$(docker ps | grep "postgres" | awk '{print $1}')

# Check if the container ID was found
if [ -z "$POSTGRES_DOCKER_ID" ]; then
    echo "Error: PostgreSQL container not found!"
    exit 1
fi

# Run the backup command
docker exec -t $POSTGRES_DOCKER_ID pg_dumpall -c -U postgres | gzip > ./db-backups/dump_$(date +"%Y-%m-%d_%H_%M_%S").gz

echo "Backup completed successfully!"
exit 0
