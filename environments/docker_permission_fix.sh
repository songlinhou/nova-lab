#!/bin/bash
docker ps > /dev/null

if [ $? -ne 0 ]; then
    echo "Permission required to run docker"
    sudo groupadd docker
    sudo gpasswd -a $USER docker
    newgrp docker
fi