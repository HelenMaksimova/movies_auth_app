from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

__all__ = (
    "AppConfigDC",
    "PostgresConfigDC",
    "RedisConfigDC",
)


class RedisConfigDC(BaseModel):
    host: str = Field("localhost", alias="HOST")
    port: int = Field(6379, alias="PORT")
    password: str | None = Field(None, alias="PASSWORD")
    db: int = Field(0, alias="DB")
    decode_responses: bool = Field(True, alias="DECODE_RESPONSES")


class PostgresConfigDC(BaseModel):
    host: str = Field("localhost", alias="HOST")
    port: int = Field(5432, alias="PORT")
    database: str = Field("postgres", alias="DATABASE")
    drivername: str = Field("postgresql+asyncpg", alias="DRIVERNAME")
    username: str | None = Field(None, alias="USERNAME")
    password: str | None = Field(None, alias="PASSWORD")
    pool_recycle: int = Field(3600, alias="POOL_RECYCLE")
    pool_pre_ping: bool = Field(True, alias="POOL_PRE_PING")
    pool_size: int = Field(10, alias="POOL_SIZE")
    max_overflow: int = Field(20, alias="MAX_OVERFLOW")
    timeout: float = Field(30.0, alias="TIMEOUT")
    statement_timeout: int = Field(0, alias="STATEMENT_TIMEOUT")
    expire_on_commit: bool = Field(True, alias="EXPIRE_ON_COMMIT")
    content_schema: str = Field("public", alias="CONTENT_SCHEMA")
    echo: bool = Field(False, alias="ECHO")

    connect_args: dict | None = None

    @model_validator(mode="after")
    def build_connect_args(self) -> "PostgresConfigDC":
        connect_args = {}
        server_settings = {}

        if self.timeout:
            connect_args["timeout"] = self.timeout

        if self.statement_timeout:
            server_settings["statement_timeout"] = str(self.statement_timeout)

        if self.content_schema and self.content_schema != "public":
            server_settings["search_path"] = f"{self.content_schema},public"

        if server_settings:
            connect_args["server_settings"] = server_settings

        self.connect_args = connect_args or None
        return self

    @property
    def url(self) -> URL:
        return URL.create(
            drivername=self.drivername,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )


class AppConfigDC(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_nested_delimiter="__",
        env_file=".env.app.local",
    )
    host: str = Field("localhost", alias="APP_HOST")
    port: int = Field(8000, alias="APP_PORT")
    project_name: str = Field("Project", alias="APP_PROJECT_NAME")
    log_level: str = Field("INFO", alias="APP_LOG_LEVEL")
    entrypoint: str = Field("app:main", alias="APP_ENTRYPOINT")
    description: str = Field("", alias="APP_DESCRIPTION")
    redis: RedisConfigDC = Field(alias="REDIS")
    postgres: PostgresConfigDC = Field(alias="DB")
