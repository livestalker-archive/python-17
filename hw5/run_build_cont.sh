#!/bin/bash

MY_DIR=$(realpath $(pwd)/../)

sudo docker run -ti --rm -v ${MY_DIR}:/root/ hw5-build /bin/bash
