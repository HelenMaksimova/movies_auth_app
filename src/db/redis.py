from logging import getLogger
from typing import Any

from redis.asyncio import (
    ConnectionError as RedisConnectionError,
    Redis,
    RedisError,
    TimeoutError as RedisTimeoutError,
)

from src.core.config import RedisConfigDC
from src.utils.interfaces import CacheClientInterface

__all__ = ("RedisClient", "get_client")


logger = getLogger()


class RedisClient(CacheClientInterface[RedisConfigDC]):
    def __init__(self, config: RedisConfigDC):
        super().__init__(config)
        self._client: Redis | None = None

    @property
    def client(self) -> Redis:
        if not self._client:
            raise ValueError(f"[{self.__class__.__name__}] Client was not set")

        return self._client

    async def ping(self) -> None:
        await self.client.ping()
        logger.info(
            "[Redis] Ping success: was connected on: %s:%s",
            self.config.host,
            self.config.port,
        )

    async def connect(self) -> None:
        try:
            if not self._client:
                self._client = Redis(
                    host=self.config.host,
                    port=self.config.port,
                    password=self.config.password,
                    db=self.config.db,
                    decode_responses=self.config.decode_responses,
                    retry_on_error=[RedisConnectionError, RedisTimeoutError],
                )

            await self.ping()

        except RedisError as err:
            logger.error("[Redis] Was not connected with error: %s", err)

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None

        logger.info("[Redis] Client was closed")

    async def get(self, key: str) -> Any:
        pass

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        pass

    async def delete(self, key: str) -> None:
        pass


async def get_client(config: RedisConfigDC) -> RedisClient:
    client = RedisClient(config)
    await client.connect()

    return client
