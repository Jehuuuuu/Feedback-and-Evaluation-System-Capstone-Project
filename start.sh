#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python nltk_downloader.py
python manage.py collectstatic --no-input
python manage.py migrate

# Start your application
python manage.py runserver 0.0.0.0:8000
