#!/bin/bash

MY_DIR=`pwd`
sudo docker run -ti --rm -v $PWD/cpython:/opt/cpython hw2 /bin/bash
