#!/bin/bash

export CONTROL=$1
maze_id=$2

python python/tester.py data/test_maze_$maze_id.txt
