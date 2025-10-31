#!/bin/bash

python manage.py migrate
python manage.py collectstatic --noinput

gunicorn dsh.wsgi:application  &
sleep 2
nginx -g "daemon off;"