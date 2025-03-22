#!/bin/bash
set -e

python manage.py makemigrations
python manage.py makemigrations consumers

python manage.py migrate
python manage.py migrate consumers

exit 0