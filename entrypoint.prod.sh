#!/usr/bin/env bash
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# NOTE: Django Select2 will break if workers > 1 ! Install and setup packages (e.g. redis) to fix.
python -m gunicorn --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-1} gsas.wsgi:application