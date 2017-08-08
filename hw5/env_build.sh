#!/usr/bin/env bash

# Create container image for build environment
sudo docker build -f Dockerfile-build -t hw5-build .
