#!/bin/bash
CONTAINER_NAME=postfix_test
docker run \
    -it \
    --rm \
    --name $CONTAINER_NAME \
    --hostname $CONTAINER_NAME \
    -v $PWD:/home/rest-mailgate \
    juanluisbaptiste/postfix /bin/bash