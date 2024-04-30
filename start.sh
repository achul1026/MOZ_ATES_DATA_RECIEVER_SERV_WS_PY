#!/bin/bash

nohup python ./server.py > /dev/null 2>&1 &
echo $! > .pid
echo "Started camera data receive server"