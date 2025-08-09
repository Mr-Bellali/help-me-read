from fastapi import FastAPI, Request
from routes import analyse
from celery_worker import write_log_celery
from celery.result import AsyncResult
from fastapi.responses import StreamingResponse
import asyncio

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
    """Endpoint that triggers the background task in Celery."""
    task = write_log_celery.delay(f"Notification sent to {email}")
    # task is a AsyncResult, a promise to a result that will be available later.
    return {"message": f"Email will be sent to {email}", "task_id": task.id}

# SSE endpoint for real-time task status
@app.get("/task_status/stream/{task_id}")
async def stream_task_status(request: Request, task_id: str):
    """Stream real-time status updates for a Celery task using SSE."""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            task_result = AsyncResult(task_id)
            if task_result.ready():
                if task_result.failed():
                    yield f"data: {{\"task_id\": \"{task_id}\", \"status\": \"failed\"}}\n\n"
                else:
                    yield f"data: {{\"task_id\": \"{task_id}\", \"status\": \"completed\", \"result\": \"{task_result.result}\"}}\n\n"
                break
            else:
                yield f"data: {{\"task_id\": \"{task_id}\", \"status\": \"in progress\"}}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """Endpoint to check the status of the task."""
    task_result = AsyncResult(task_id)  # Get the task result using the task ID
    if task_result.ready():  # If the task is done
        return {"task_id": task_id, "status": "completed", "result": task_result.result}
    elif task_result.failed():  # If the task failed
        return {"task_id": task_id, "status": "failed"}
    else:  # If the task is still in progress
        return {"task_id": task_id, "status": "in progress"}