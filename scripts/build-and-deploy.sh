#!/bin/bash

# Get the current highest tag number from docker stack ps for karl services
# Assuming that the services follow the naming convention karl/SERVICE:TAG and that TAG is numerical
highest_tag=$(docker stack ps karl | grep -oP 'karl/\S+:\K\d+' | sort -nr | head -n 1)

# Increment the tag number
let new_tag=highest_tag+1

# Export the TAG and FRONTEND_ENV variables
export TAG=$new_tag
export FRONTEND_ENV=production

# Run the build script
bash ./scripts/build.sh &&

# Set other variables and run the deploy script
DOMAIN=karl.qanta.org \
TRAEFIK_TAG=karl \
STACK_NAME=karl \
TAG=$new_tag \
bash ./scripts/deploy.sh