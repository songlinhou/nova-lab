#!/bin/bash
USER_NAME=$(whoami)
source ../docker_permission_fix.sh
CONTAINER_NAME="r_jupyter:$USER_NAME"
mkdir -p container_names
echo "Jupyter Notebook with R Language Image Builder"

echo "Input the name of container"
read CONTAINER_NAME_PREFIX
CONTAINER_NAME="$CONTAINER_NAME_PREFIX:$USER_NAME"

echo "Using $CONTAINER_NAME as container name"
sleep 3
docker build -f dockerfile -t $CONTAINER_NAME .

if [ $? -eq 0 ]
then
    echo "Image $CONTAINER_NAME is built successfully"
    echo $CONTAINER_NAME_PREFIX > "container_names/$USER_NAME"
else
    echo "Error in building image $CONTAINER_NAME"
fi