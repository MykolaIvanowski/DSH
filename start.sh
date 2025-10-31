#!/bin/bash

# Зapply migration
python manage.py migrate --noinput

# collect static
python manage.py collectstatic --noinput

# start Gunicorn
gunicorn dsh.wsgi:application
sleep 3

echo "🌐 Starting nginx..."
nginx -g "daemon off;"