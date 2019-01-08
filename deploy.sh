#!/bin/sh

find -name "*.pyc" -delete
scp -r abippity abap@$IP:
scp -r sapiness abap@$IP:
