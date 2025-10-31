#!/bin/bash

python manage.py migrate

gunicorn dsh.wsgi:application --bind 127.0.0.1:8000 &
nginx -g "daemon off;"