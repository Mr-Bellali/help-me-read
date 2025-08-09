from fastapi import FastAPI
from routes import analyse
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