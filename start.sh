#!/bin/bash
set -e
# Зapply migration
python manage.py migrate --noinput

# collect static
python manage.py collectstatic --noinput

# start Gunicorn
dsh.wsgi:application --workers 3 --bind 127.0.0.1:8000
sleep 3

echo "🌐 Starting nginx..."
nginx -t
exec nginx -g "daemon off;"
