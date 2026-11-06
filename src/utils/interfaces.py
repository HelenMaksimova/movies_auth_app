from abc import ABC, abstractmethod
from typing import Any

__all__ = (
    "CacheClientInterface",
    "ConnectClientInterface",
    "DatabaseClientInterface",
    "ServiceInterface",
)


class ConnectClientInterface[ConfigDC](ABC):
    def __init__(self, config: ConfigDC):
        self.config = config

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def ping(self) -> None:
        pass


class CacheClientInterface[ConfigDC](ConnectClientInterface[ConfigDC]):
    @abstractmethod
    async def get(self, key: str) -> Any:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass


class DatabaseClientInterface[ConfigDC](ConnectClientInterface[ConfigDC]):
    pass


class ServiceInterface[
    DatabaseClient: DatabaseClientInterface,
    CacheClient: CacheClientInterface,
](ABC):
    def __init__(self, db: DatabaseClient, cache: CacheClient):
        self.db = db
        self.cache = cache
