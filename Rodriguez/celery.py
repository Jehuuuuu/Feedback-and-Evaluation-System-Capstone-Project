from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
import multiprocessing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rodriguez.settings')

app = Celery('Rodriguez')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
multiprocessing.set_start_method('spawn')
