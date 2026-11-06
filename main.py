from contextlib import asynccontextmanager
from logging import config as log_config

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse
from starlette.types import Lifespan
from uvicorn import run

from src.api.v1.health.views import router as health_router
from src.core.config import AppConfigDC
from src.core.log_settings import LOGGING
from src.db.postgres import get_client as get_postgres_client
from src.db.redis import get_client as get_redis_client

app_config = AppConfigDC()
log_config.dictConfig(LOGGING)


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    app.state.redis = await get_redis_client(app_config.redis)
    app.state.postgres = await get_postgres_client(app_config.postgres)

    yield

    if app.state.redis:
        await app.state.redis.disconnect()

    if app.state.postgres:
        await app.state.postgres.disconnect()


def set_routers(app: FastAPI):
    v1_router = APIRouter(prefix="/auth/v1")
    v1_router.include_router(
        health_router,
        prefix="/health",
        tags=["AUTH - версия v1", "Health check"],
    )

    app.include_router(v1_router)


def create_app(
    config: AppConfigDC,
    lifespan: Lifespan | None = None,
    openapi_tags: list[dict] | None = None,
):
    app = FastAPI(
        title=config.project_name,
        description=config.description,
        docs_url="/auth/docs",
        openapi_url="/auth/openapi.json",
        openapi_tags=openapi_tags,
        default_response_class=JSONResponse,
        lifespan=lifespan,
    )

    set_routers(app)

    return app


app = create_app(
    app_config,
    db_lifespan,
    [
        {
            "name": "AUTH",
            "description": "Общий список эндпоинтов AUTH",
        },
    ],
)


if __name__ == "__main__":
    run(
        app_config.entrypoint,
        host=app_config.host,
        port=app_config.port,
        log_config=LOGGING,
        log_level=app_config.log_level,
    )
