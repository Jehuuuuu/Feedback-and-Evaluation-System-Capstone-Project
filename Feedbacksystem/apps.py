from django.apps import AppConfig
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

class FeedbacksystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Feedbacksystem'

    def ready(self):
        """
        Starts the BackgroundScheduler and schedules any default tasks.
        Ensures proper cleanup on server shutdown.
        """
        from .views import close_evaluations, approve_pending_evaluations

        # Initialize the scheduler
        scheduler = BackgroundScheduler()

        # Start the scheduler
        scheduler.start()

        # Ensure the scheduler shuts down cleanly on server exit
        atexit.register(lambda: scheduler.shutdown(wait=False))
