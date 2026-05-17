#!/usr/bin/env bash
set -e

export RECIPE_DATA_DIR="${RECIPE_DATA_DIR:-/tmp/local_data}"

export BACKGROUND_RECIPE_DATA_DOWNLOAD=False
python mysite/manage.py migrate --noinput
python mysite/manage.py collectstatic --noinput

export BACKGROUND_RECIPE_DATA_DOWNLOAD=True
gunicorn mysite.wsgi:application --bind "0.0.0.0:${PORT:-8080}"
