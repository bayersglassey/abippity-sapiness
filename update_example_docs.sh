#!/bin/sh
set -e

CMD='from documents.utils import update_example_docs; print(update_example_docs())'
ssh abap@$IP './venv/bin/python sapiness/manage.py shell -c '"'$CMD'"
