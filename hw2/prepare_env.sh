#!/bin/bash
sudo docker build -t hw2 .
git clone https://github.com/python/cpython.git
cd cpython
git checkout 2.7
