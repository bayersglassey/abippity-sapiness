#!/bin/sh
set -e

./bump.sh
./restart.sh
./update_example_docs.sh
