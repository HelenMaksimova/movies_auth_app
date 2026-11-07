from fastapi import Request, Response
from sqlalchemy import select
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from src.models.realm.models import Realm


class ContextMiddleware(BaseHTTPMiddleware):
    def _get_access_token(self, request: Request) -> str | None:
        auth = request.headers.get("Authorization")

        if auth and auth.lower().startswith("bearer "):
            return auth.split(" ", 1)[1]

        return request.cookies.get("access_token")

    async def _get_realm(self, request: Request) -> Realm | None:
        realm_name = request.headers.get("X-Realm-Name")
        if not realm_name:
            return None

        query = select(Realm).where(Realm.name == realm_name)
        async with request.app.state.postgres.get_session() as session:
            return await session.scalar(query)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request.state.access_token = self._get_access_token(request)
        request.state.realm = await self._get_realm(request)

        return await call_next(request)
