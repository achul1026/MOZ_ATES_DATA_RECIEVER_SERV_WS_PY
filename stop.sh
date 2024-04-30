#!/bin/bash

kill -15 $(cat .pid)

echo "" > .pid