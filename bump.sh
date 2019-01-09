#!/bin/sh
set -e

find -name "*.pyc" -delete
scp -r abippity abap@$IP:
scp -r sapiness abap@$IP:
