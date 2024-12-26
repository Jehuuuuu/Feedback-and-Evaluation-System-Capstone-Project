from django.core.management.base import BaseCommand
from Feedbacksystem.scheduler import scheduler
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run the APScheduler."

    def handle(self, *args, **options):
        if not scheduler.running:
            self.stdout.write("Starting the APScheduler...")
            scheduler.start()
            self.stdout.write("Scheduler started successfully!")
        else:
            self.stdout.write("Scheduler is already running.")
