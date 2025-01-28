#!/bin/bash

python manage.py makemigrations users
python manage.py migrate users
python manage.py makemigrations files
python manage.py migrate files
python manage.py migrate

exec "$@"