"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, engine
from .routers import tasks, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Tasks API",
    description="A REST API for task management with JWT authentication.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/", tags=["health"])
def root():
    return {"message": "Tasks API is running", "docs": "/docs"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
