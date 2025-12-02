"""
FastAPI application entrypoint for Smart Campus Assistant.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import Base, engine
from .routers import core as core_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler:
    - create DB tables on startup (for quick local dev)
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core_router.router, prefix=settings.api_prefix)



