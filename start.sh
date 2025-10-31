#!/bin/bash

python manage.py migrate
python manage.py collectstatic --noinput

gunicorn dsh.wsgi:application --bind 127.0.0.1:8000 &
nginx -g "daemon off;"