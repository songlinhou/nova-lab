#!/bin/bash
USER_NAME=$(whoami)
CONTAINER_NAME=$(cat "container_names/$USER_NAME")

echo "Container Name: $CONTAINER_NAME"
echo "###### Jupyter Notebook ######"
echo "1) Restart notebook without GPU"
echo "2) Restart notebook with GPU"

echo "###### Jupyter Lab ######"
echo "3) Restart lab without GPU"
echo "4) Restart lab with GPU"

read CHOICE

# RUN_JUPYTER_CMD="jupyter notebook password  && jupyter notebook --port 8888 --ip 0.0.0.0 --no-browser --allow-root"
RUN_NOTEBOOK_CMD="bash /run_notebook.sh"
RUN_LAB_CMD="bash /run_lab.sh"

# RUN_NOTEBOOK_CMD="bash"

if [ $CHOICE -eq 1 ]
then
    docker run -it -p 8811:8888 -v ~:/src -v cache:/root/.cache $CONTAINER_NAME $RUN_NOTEBOOK_CMD
elif [ $CHOICE -eq 2 ]
then
    docker run -it -p 8811:8888 --gpus all -v ~:/src -v cache:/root/.cache $CONTAINER_NAME $RUN_NOTEBOOK_CMD
elif [ $CHOICE -eq 3 ]
then
    docker run -it -p 8811:8888 -v ~:/src -v cache:/root/.cache $CONTAINER_NAME $RUN_LAB_CMD
elif [ $CHOICE -eq 4 ]
then
    docker run -it -p 8811:8888 --gpus all -v ~:/src -v cache:/root/.cache $CONTAINER_NAME $RUN_LAB_CMD
else
    echo "Wrong choice."
fi
    