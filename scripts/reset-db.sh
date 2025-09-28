#!/bin/bash

# Reset Database and Restart Development Environment
# This script will:
# 1. Stop all containers
# 2. Remove the database volume (dropping all data)
# 3. Start the stack fresh
# 4. Enter the backend container and run start-reload.sh

set -e

echo "🔄 Resetting database and restarting development environment..."

# Stop all containers
echo "📦 Stopping all containers..."
docker compose down

# Remove the database volume to completely reset the database
echo "🗑️  Removing database volume (this will delete ALL data)..."
docker volume rm karl-flashcards-web-app_app-db-data 2>/dev/null || echo "Volume already removed or doesn't exist"

# Start the stack fresh
echo "🚀 Starting fresh stack..."
docker compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Enter backend container and run start-reload.sh
echo "🔧 Entering backend container and starting development server..."
echo "💡 The development server will start with live reloading enabled."
echo "💡 Press Ctrl+C to stop the server, but the container will remain running."
echo ""

docker compose exec backend bash /start-reload.sh
