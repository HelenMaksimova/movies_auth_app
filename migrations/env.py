import asyncio
from logging.config import fileConfig

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from src.core.config import AppConfigDC
from src.models.pg_base import Base


config = context.config
app_config = AppConfigDC()

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


async def ensure_schema_exists(engine, schema_name):
    async with engine.connect() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        await conn.commit()


def run_migrations_offline() -> None:
    context.configure(
        url=app_config.postgres.url,
        target_metadata=target_metadata,
        literal_binds=True,
        version_table_schema=app_config.postgres.content_schema,
        include_schemas=True
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = create_async_engine(
        app_config.postgres.url,
        connect_args=app_config.postgres.connect_args
    )

    await ensure_schema_exists(connectable, app_config.postgres.content_schema)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
