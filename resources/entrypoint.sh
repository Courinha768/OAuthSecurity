#!/bin/bash
set -e

python manage.py makemigrations
python manage.py makemigrations authentication

python manage.py migrate
python manage.py migrate authentication

exit 0