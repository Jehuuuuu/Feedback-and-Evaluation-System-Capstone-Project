from django.apps import AppConfig
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore 
import environ

env = environ.Env()

environ.Env.read_env()


class FeedbacksystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Feedbacksystem'

    def ready(self):
        from .views import close_evaluations, approve_pending_evaluations


        # Configure job store to use PostgreSQL
        jobstores = {
           'default': SQLAlchemyJobStore(url=env('DATABASE_URL'))
        }

        scheduler = BackgroundScheduler(jobstores=jobstores)

        # Start the scheduler
        scheduler.start()

        # Ensure the scheduler shuts down cleanly on server exit
        atexit.register(lambda: scheduler.shutdown(wait=False))


