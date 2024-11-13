from celery import shared_task
from django.utils import timezone
from .models import Event

@shared_task
def deactivate_expired_evaluations():
    # Filter for active evaluations whose end datetime has passed
    expired_evaluations = Event.objects.filter(
        evaluation_status=True,
        evaluation_end_datetime__lte=timezone.now()
    )
    # Update each expired evaluation's status to inactive
    for evaluation in expired_evaluations:
        evaluation.evaluation_status = False
        evaluation.save()

@shared_task
def add(x, y):
    return x + y