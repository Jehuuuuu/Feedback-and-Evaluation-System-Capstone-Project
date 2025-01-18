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

        from .utils import sentiment_pipeline
        try:
            # Preload the sentiment analysis model at startup
            sentiment_pipeline.get_pipeline()
            logger.info("Sentiment analysis model loaded successfully at startup.")
            print("Sentiment analysis model loaded successfully at startup.")
        except Exception as e:
            logger.error(f"Error loading sentiment analysis model: {e}")
