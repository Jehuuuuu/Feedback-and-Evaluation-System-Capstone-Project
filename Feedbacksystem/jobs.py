import logging
from Feedbacksystem.models import EvaluationStatus, LikertEvaluation, Event
from datetime import timedelta, datetime
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def close_evaluations():
    updated_evaluation_status = EvaluationStatus.objects.filter(evaluation_status='In Progress').update(evaluation_status='Closed')
    print(updated_evaluation_status)

def approve_pending_evaluations():
    """Approve all pending evaluations."""
    today = datetime.today().date()
    updated_count = LikertEvaluation.objects.filter(admin_status='Pending').update(admin_status='Approved')
    print(f"{updated_count} evaluations approved on {today}.")

def start_event_evaluations(event_pk):
    """Approve all pending evaluations."""
    event = Event.objects.get(pk=event_pk)
    event.evaluation_status = 'Ongoing'
    event.save()
    logger.info(f"Started evaluations for {event.title}")

def end_event_evaluations(event_pk):
    """Approve all pending evaluations."""
    event = Event.objects.get(pk=event_pk)
    event.evaluation_status = 'Closed'
    event.save()
    logger.info(f"Ended evaluations for {event.title}")
