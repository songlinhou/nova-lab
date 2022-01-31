#!/bin/bash
IP_FILE="store/ip.txt"
USER_FILE="store/user.txt"

## generate the store folder if not exists
if [ ! -d "store" ]
then
    # create the store folder
    mkdir store
fi

if [ ! -f "${IP_FILE}" ]
then
    touch "${IP_FILE}"
fi

if [ ! -f "${USER_FILE}" ]
then
    touch "${USER_FILE}"
fi

TARGET_IP=$(cat store/ip.txt)
USER=$(cat store/user.txt)


if [ -z "$TARGET_IP" ]
then
    echo "You did not provide a valid IP for the server. Please update your server IP address in file ${IP_FILE} and re-run this script."
    exit 1
fi

if [ -z "$USER" ]
then
    echo "You did not provide a valid user name to access the server. Please update your user name in file ${USER_FILE} and re-run this script."
    exit 1
fi

IS_WIN=1 # check if this script is on windows

## check if it is on windows
# if [[ "$OSTYPE" == "msys"* ]]
# then
#     # using gitbash
#     IS_WIN=1
# elif [[ "$OSTYPE" == "cygwin"* ]]
# then
#     # emulation on windows
#     IS_WIN=1
# else
#     IS_WIN=0
# fi

echo "###################################################"
echo "Data Transfer (You can update info in store folder)"
echo "###################################################"
echo "Choose option (Current User: ${USER})"


echo "1) Download from \"${TARGET_IP}\" to local"
echo "2) Upload a local file or folder to \"${TARGET_IP}\""


read -p "choice=" option


if [[ $option -eq 1 ]]
then
    echo "Input absolute filepath in the server:"
    read -p "path=" filepath
    if [[ $IS_WIN -eq 1 ]]
    then
        scp -r "${USER}@${TARGET_IP}:${filepath}" .
    else
        rsync -av --progress "${USER}@${TARGET_IP}:${filepath}" .
    fi

elif [[ $option -eq 2 ]]
then
    echo "Input local filepath you want to upload:"
    read -p "path=" filepath
    if [[ $IS_WIN -eq 1 ]]
    then
        scp -r ${filepath} "${USER}@${TARGET_IP}:~"
    else
        rsync -av --progress ${filepath} "${USER}@${TARGET_IP}:~"
    fi

else
    echo "only 1 or 2 is acceptable"
fi
