#! /usr/bin/env sh

# Exit in case of error
set -e

TAG=$1
FRONTEND_ENV=production \
docker-compose \
-f docker-compose.yml \
build

DOMAIN=karl.qanta.org \
TRAEFIK_TAG=karl \
STACK_NAME=karl \
TAG=$1 \
docker-compose \
-f docker-compose.yml \
config > docker-stack.yml

docker stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME}"