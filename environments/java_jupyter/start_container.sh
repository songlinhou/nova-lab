#!/bin/bash
USER_NAME=$(whoami)
source ../docker_permission_fix.sh
CONTAINER_NAME_PREFIX=$(cat "container_names/$USER_NAME")
CONTAINER_NAME="$CONTAINER_NAME_PREFIX:$USER_NAME"
echo "Container Name: $CONTAINER_NAME"
echo "Starting ..."

sleep 3

docker rm -f $CONTAINER_NAME_PREFIX > /dev/null
echo "Open: http://localhost:8811" && echo "#################" && docker run -it -p 8811:8888 -v ~:/home/jovyan/work --name $CONTAINER_NAME_PREFIX $CONTAINER_NAME