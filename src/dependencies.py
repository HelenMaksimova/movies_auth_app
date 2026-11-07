from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.services.realm import RealmService, get_realm_service

__all__ = (
    "DepPostgresSession",
    "DepRealmService",
)


DepPostgresSession = Annotated[AsyncSession, Depends(get_session)]
DepRealmService = Annotated[RealmService, Depends(get_realm_service)]
