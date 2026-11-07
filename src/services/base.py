from typing import TypeVar

from sqlalchemy import ScalarResult, Select

from src.db.postgres import PostgresClient
from src.db.redis import RedisClient
from src.utils.interfaces import ServiceInterface

__all__ = ("BaseService",)

_T = TypeVar("_T")


class BaseService(ServiceInterface[PostgresClient, RedisClient]):
    async def get_scalar(self, query: Select[_T | tuple[_T]]) -> _T | None:
        async with self.db.get_session() as session:
            return await session.scalar(query)

    async def get_scalars(self, query: Select[_T | tuple[_T]]) -> ScalarResult:
        async with self.db.get_session() as session:
            return await session.scalars(query)
