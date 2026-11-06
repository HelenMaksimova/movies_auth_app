from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session

__all__ = ("DepPostgresSession",)


DepPostgresSession = Annotated[AsyncSession, Depends(get_session)]
