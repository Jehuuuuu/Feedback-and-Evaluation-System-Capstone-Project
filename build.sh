#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python -m nltk.downloader stopwords && gunicorn Rodriguez.wsgi:application
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

# Start your application
python manage.py runserver 0.0.0.0:8000
