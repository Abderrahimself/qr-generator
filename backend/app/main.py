from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import redis.asyncio as redis
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import engine
from app.logging_config import setup_logging
from app.middleware import RequestIDMiddleware
from app.repositories.storage_repo import create_presign_client, create_s3_client
from app.routes import health, qr

setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    logger.info("starting_qr_generator_api")

    valkey_client = redis.Redis(
        host=settings.valkey_host,
        port=settings.valkey_port,
        decode_responses=False,
    )
    s3_client = create_s3_client()
    presign_client = create_presign_client()

    app.state.valkey_client = valkey_client
    app.state.s3_client = s3_client
    app.state.presign_client = presign_client

    yield

    # Graceful shutdown — close all connections
    logger.info("shutting_down", detail="closing valkey connection")
    await valkey_client.aclose()

    logger.info("shutting_down", detail="disposing database pool")
    await engine.dispose()

    # boto3 clients have no explicit close() — the underlying HTTP session
    # is cleaned up on garbage collection
    logger.info("shutdown_complete")


app = FastAPI(
    title="QR Generator",
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware — added in reverse order (last added = outermost in request lifecycle)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)

app.include_router(health.router)
app.include_router(qr.router)

# Prometheus metrics — instruments all routes and exposes /metrics
Instrumentator().instrument(app).expose(app)
