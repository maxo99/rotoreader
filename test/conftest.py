from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer

from rotoreader.adapters.postgres_client import PostgresClient


class PgVectorContainer(PostgresContainer):
    """Custom PostgreSQL container with pgvector extension."""

    def __init__(self, image: str = "pgvector/pgvector:pg18", **kwargs):
        super().__init__(image=image, **kwargs)


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PgVectorContainer, None, None]:
    with PgVectorContainer(
        image="pgvector/pgvector:pg18",
        dbname="rotoreader_test",
        username="test_user",
        password="test_password",
        driver=None,  # Don't specify driver, we'll construct the URL manually
    ) as container:
        # Wait for container to be ready
        container.get_connection_url()
        yield container


@pytest.fixture(scope="session")
def db_config(postgres_container: PgVectorContainer) -> dict[str, Any]:
    """Database configuration from testcontainer."""
    # Construct async connection URL with asyncpg driver
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    database = postgres_container.dbname
    username = postgres_container.username
    password = postgres_container.password

    # Use asyncpg driver for async connections
    async_url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"

    return {
        "host": host,
        "port": port,
        "database": database,
        "username": username,
        "password": password,
        "url": async_url,
    }


@pytest_asyncio.fixture(scope="function")
async def postgres_client(
    db_config: dict[str, Any],
) -> AsyncGenerator[PostgresClient, None]:
    # Import and store original client
    import rotoreader.service

    original_client = rotoreader.service.PG_CLIENT

    client = None
    try:
        # Create a new client for each test with the current event loop
        # Use NullPool to avoid connection pool issues across event loops in tests
        client = PostgresClient(db_url=db_config["url"], use_null_pool=True)

        # Setup: Create pgvector extension and initialize tables
        async with client.engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(lambda sync_conn: sync_conn.execute(text("SELECT 1")))

        # Initialize tables
        await client.initialize()

        # Monkey patch the global PG_CLIENT
        rotoreader.service.PG_CLIENT = client

        yield client

    finally:
        # Restore original client
        rotoreader.service.PG_CLIENT = original_client
        if client:
            await client.close()
