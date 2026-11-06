from collections.abc import AsyncGenerator
from logging import getLogger

from asyncpg import PostgresConnectionError, PostgresError
from backoff import expo, on_exception
from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import PostgresConfigDC
from src.utils.interfaces import DatabaseClientInterface

__all__ = ("PostgresClient", "get_client", "get_session")

logger = getLogger()


class PostgresClient(DatabaseClientInterface[PostgresConfigDC]):
    def __init__(self, config: PostgresConfigDC) -> None:
        super().__init__(config)
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker | None = None

    @property
    def engine(self) -> AsyncEngine:
        if not self._engine:
            raise ValueError(f"[{self.__class__.__name__}] Engine was not set")

        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker:
        if not self._session_factory:
            raise ValueError(
                f"[{self.__class__.__name__}] Session factory was not set"
            )

        return self._session_factory

    @on_exception(expo, PostgresConnectionError, max_tries=5)
    async def ping(self) -> None:
        async with self.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info(
            "[Postgres] Was connected on: %s:%s",
            self.config.host,
            self.config.port,
        )

    async def connect(self) -> None:
        try:
            if not self._engine:
                self._engine = create_async_engine(
                    self.config.url,
                    echo=self.config.echo,
                    pool_size=self.config.pool_size,
                    max_overflow=self.config.max_overflow,
                    pool_pre_ping=self.config.pool_pre_ping,
                    pool_recycle=self.config.pool_recycle,
                    connect_args=self.config.connect_args,
                )

            if not self._session_factory:
                self._session_factory = async_sessionmaker(
                    self._engine,
                    class_=AsyncSession,
                    expire_on_commit=self.config.expire_on_commit,
                )

            await self.ping()

        except PostgresError as err:
            logger.error("[Postgres] Was not connected with error: %s", err)

    async def disconnect(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

        logger.info("[Postgres] Client was closed")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


async def get_client(config: PostgresConfigDC) -> PostgresClient | None:
    client = PostgresClient(config)
    await client.connect()

    return client


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async for session in request.app.state.postgres.get_session():
        yield session
