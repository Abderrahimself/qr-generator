import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.repositories.storage_repo import create_s3_client
from app.routes import health, qr

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    logger.info("Starting QR Generator API")

    # Valkey connection
    valkey_client = redis.Redis(
        host=settings.valkey_host,
        port=settings.valkey_port,
        decode_responses=False,
    )

    # S3 client for Garage
    s3_client = create_s3_client()

    # Store clients on app state for access in dependencies
    app.state.valkey_client = valkey_client
    app.state.s3_client = s3_client

    yield

    # Shutdown
    await valkey_client.aclose()
    await engine.dispose()
    logger.info("Shutting down QR Generator API")


app = FastAPI(
    title="QR Generator",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(qr.router)
