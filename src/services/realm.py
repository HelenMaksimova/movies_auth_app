from functools import lru_cache
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from starlette.requests import Request

from src.db.postgres import PostgresClient
from src.db.redis import RedisClient
from src.models.realm.models import Realm, RealmCredentials, RealmKeys
from src.services.base import BaseService

__all__ = (
    "RealmService",
    "get_realm_service",
)


class RealmService(BaseService):
    async def authenticate(self, request: Request) -> None:
        token: str | None = getattr(request.state, "access_token", None)
        realm: Realm | None = getattr(request.state, "realm", None)

        if realm and token:
            token_hash = RealmCredentials.hash_token(token)

            query = select(RealmCredentials).where(
                RealmCredentials.token == token_hash
            )
            credentials = await self.get_scalar(query)

            if credentials and credentials.is_valid():
                return

            raise HTTPException(403, "access denied")

        else:
            raise HTTPException(401, "unauthorized")

    async def create_realm_keys(self, realm_id: UUID) -> RealmKeys:
        async with self.db.get_session() as session, session.begin():
            keys = RealmKeys.create_keys(realm_id)
            session.add(keys)
            return keys


@lru_cache
def _make_service(
    pg_client: PostgresClient, redis_client: RedisClient
) -> RealmService:
    return RealmService(pg_client, redis_client)


def get_realm_service(request: Request) -> RealmService:
    return _make_service(request.app.state.postgres, request.app.state.redis)
