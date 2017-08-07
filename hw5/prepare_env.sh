#!/bin/bash
sudo docker build -f Dockerfile-build -t hw5-build .
sudo docker build -t hw5 .
