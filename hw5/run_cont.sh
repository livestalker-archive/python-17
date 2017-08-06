#!/bin/bash

MY_DIR=`pwd`
sudo docker run --rm -p :8080:80 \
                --privileged \
                -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
                --name hw5-cont -d hw5
sudo docker exec -i -t hw5-cont /bin/bash
