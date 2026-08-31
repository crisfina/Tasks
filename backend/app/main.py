from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.categories import router as categories_router
from app.api.routers.events import router as events_router
from app.api.routers.households import router as households_router
from app.api.routers.point_transactions import (
    router as point_transactions_router,
)
from app.api.routers.rooms import router as rooms_router
from app.api.routers.task_occurrences import (
    router as task_occurrences_router,
)
from app.api.routers.tasks import router as tasks_router
from app.api.routers.user_statistics import (
    router as user_statistics_router,
)
from app.api.routers.users import router as users_router
from app.core.exception_handlers import app_error_handler
from app.core.exceptions import AppError


app = FastAPI(
    title="Tasks API",
    description="API for managing tasks",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://crisfina.github.io",
        "https://tasks-q493amxvd-cristina-s-projects9.vercel.app",
        "https://tasks-psi-seven.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    AppError,
    app_error_handler,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(households_router)
app.include_router(categories_router)
app.include_router(rooms_router)
app.include_router(tasks_router)
app.include_router(task_occurrences_router)
app.include_router(events_router)
app.include_router(point_transactions_router)
app.include_router(user_statistics_router)


@app.get("/")
def root():
    return {
        "name": "Tasks API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }