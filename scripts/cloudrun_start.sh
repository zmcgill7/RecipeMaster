#!/usr/bin/env bash
set -e

export RECIPE_DATA_DIR="${RECIPE_DATA_DIR:-/tmp/local_data}"

python scripts/download_recipe_data.py
python mysite/manage.py migrate --noinput
python mysite/manage.py collectstatic --noinput

gunicorn mysite.wsgi:application --bind "0.0.0.0:${PORT:-8080}"
