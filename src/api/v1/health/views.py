from datetime import UTC, datetime
from typing import Any

from asyncpg import PostgresError
from fastapi import APIRouter, Request, Response, status as http_status
from redis import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.dependencies import DepPostgresSession

__all__ = ("router",)

router = APIRouter()


@router.get("/check")
async def check(
    request: Request,
    session: DepPostgresSession,
    response: Response,
) -> dict[str, Any]:
    status = "healthy"
    response.status_code = http_status.HTTP_200_OK

    try:
        await session.execute(text("SELECT 1"))
        await request.app.state.redis.ping()
    except (SQLAlchemyError, PostgresError, RedisError):
        status = "unhealthy"
        response.status_code = http_status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
    }
