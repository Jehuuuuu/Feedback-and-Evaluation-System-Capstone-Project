import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_job():
    logger.info("Scheduler is running in production environment.")
