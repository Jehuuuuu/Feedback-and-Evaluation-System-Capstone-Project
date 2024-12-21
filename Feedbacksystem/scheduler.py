from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import atexit
import environ

env = environ.Env()
environ.Env.read_env()

# Configure job store to use PostgreSQL
jobstores = {
    'default': SQLAlchemyJobStore(url=env('DATABASE_URL'))
}

# Initialize scheduler globally
scheduler = BackgroundScheduler(jobstores=jobstores)

# Clean shutdown on server exit
atexit.register(lambda: scheduler.shutdown(wait=False))
