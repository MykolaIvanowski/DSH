#!/bin/bash

# Зapply migration
python manage.py migrate --noinput

# collect static
python manage.py collectstatic --noinput

# start Gunicorn
gunicorn dsh.wsgi:application --bind 0.0.0.0:8000 &
sleep 2
# start nginx
echo "🌐 Starting nginx..."
nginx -g "daemon off;"