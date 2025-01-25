from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class FeedbacksystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Feedbacksystem'

    def ready(self):
        from .scheduler import scheduler

        scheduler.start()
 
        print("Scheduler started successfully!")
