# Followed the tutorialin medium: https://medium.com/@hitorunajp/celery-and-background-tasks-aebb234cae5d

from celery import Celery
import time

# Configure Celery to use Redis as the message broker
celery = Celery(
    "worker", # This is the name of your Celery applicarion
    broker="redis://localhost:6379/0", # This is the Redis connection string
    backend="redis://localhost:6379/0", # Optional, for storing task results
)

@celery.task
def write_log_celery(message: str):
    time.sleep(30)
    with open("log_celery.txt", "a") as f:
        f.write(f"{message}/n")
    return f"Task completed: {message}"