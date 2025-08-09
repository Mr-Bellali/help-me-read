from fastapi import FastAPI
from routes import analyse
from celery_worker import write_log_celery
app = FastAPI(
    title="API for help me read project"
)

app.include_router(analyse.router)

@app.get("/", response_description="Root Path", tags=["Healthcheck"])
async def root():
    """
    Root endpoint.
    """
    return {"message": "Hello from api"}

# Play with celery to practice
@app.post("/notify")
async def notify_user(email: str):
    write_log_celery.delay(f"Notification sent to {email}")
    return {"message": f"Email will be sent to {email}"}