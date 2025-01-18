from django.apps import AppConfig


class FeedbacksystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Feedbacksystem'

    def ready(self):
        from . import utils
        from .scheduler import scheduler

        scheduler.start()
 
        print("Scheduler started successfully!")
