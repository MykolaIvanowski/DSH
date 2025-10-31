#!/bin/bash

# Зapply migration
python manage.py migrate --noinput

# collect static
python manage.py collectstatic --noinput

# start Gunicorn
gunicorn dsh.wsgi:application  &
sleep 2
# start nginx
echo "🌐 Starting nginx..."
nginx -g "daemon off;"