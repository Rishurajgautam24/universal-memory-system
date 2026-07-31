from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ums.config import settings
from ums.distillation.pipeline import DistillationPipeline
from ums.gateway.exceptions import UMSException
from ums.gateway.middleware.auth import AuthMiddleware
from ums.gateway.middleware.rate_limit import RateLimitMiddleware
from ums.gateway.routes import explain, observe, recall, reflect, search, timeline
from ums.llm.openrouter import OpenRouterProvider
from ums.memory.candidate import MemoryEngine
from ums.observation.engine import ObservationEngine
from ums.recall.engine import RecallEngine
from ums.storage.sqlite import SQLiteStorage

logger = logging.getLogger(__name__)


class AppContext:
    def __init__(
        self,
        storage: SQLiteStorage | None = None,
        llm: OpenRouterProvider | None = None,
        observation_engine: ObservationEngine | None = None,
        memory_engine: MemoryEngine | None = None,
        recall_engine: RecallEngine | None = None,
        distillation_pipeline: DistillationPipeline | None = None,
    ):
        self.storage = storage or SQLiteStorage(settings.database_url)
        self.llm = llm or OpenRouterProvider()
        self.observation_engine = observation_engine or ObservationEngine(
            llm=self.llm,
            storage=self.storage,
            min_confidence=settings.min_observation_confidence,
            max_observations=settings.max_observations_per_conversation,
        )
        self.memory_engine = memory_engine or MemoryEngine(storage=self.storage)
        self.recall_engine = recall_engine or RecallEngine(storage=self.storage)
        self.distillation_pipeline = distillation_pipeline or DistillationPipeline(
            storage=self.storage,
            memory_engine=self.memory_engine,
            batch_size=settings.distillation_batch_size,
        )


app_ctx: AppContext | None = None


def get_ctx() -> AppContext:
    global app_ctx
    if app_ctx is None:
        app_ctx = AppContext()
    return app_ctx


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting up")
    ctx = get_ctx()
    await ctx.storage.initialize()
    yield
    logger.info("shutting down")
    await ctx.storage.close()


def create_app() -> FastAPI:
    app = FastAPI(title="UMS Memory Gateway", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    rate_limits = {
        "POST:/v1/observe": settings.rate_limit_observe_per_hour,
        "POST:/v1/recall": settings.rate_limit_recall_per_hour,
        "POST:/v1/search": settings.rate_limit_search_per_hour,
        "GET:/v1/timeline": settings.rate_limit_timeline_per_hour,
        "POST:/v1/explain": settings.rate_limit_explain_per_hour,
        "POST:/v1/reflect": settings.rate_limit_reflect_per_hour,
    }
    app.add_middleware(RateLimitMiddleware, limits=rate_limits)
    app.add_middleware(AuthMiddleware, api_key=settings.admin_api_key)

    app.include_router(observe.router)
    app.include_router(recall.router)
    app.include_router(search.router)
    app.include_router(timeline.router)
    app.include_router(explain.router)
    app.include_router(reflect.router)

    @app.exception_handler(UMSException)
    async def ums_exception_handler(request: Request, exc: UMSException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "ok": False,
                "error": exc.error,
                "message": exc.message,
                "meta": {"request_id": str(uuid4())},
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled exception")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "internal_error",
                "message": "Internal server error",
                "meta": {"request_id": str(uuid4())},
            },
        )

    @app.get("/health")
    async def health():
        ctx = get_ctx()
        db_ok = await ctx.storage.health_check()
        return {"status": "ok" if db_ok else "degraded", "database": "connected" if db_ok else "error"}

    return app
