#!/bin/sh
set -e

scp uwsgi/sapiness.ini root@$IP:/etc/uwsgi.d/
echo "Stopping uwsgi..."
ssh root@$IP systemctl stop uwsgi
echo "Starting uwsgi..."
ssh root@$IP systemctl start uwsgi
