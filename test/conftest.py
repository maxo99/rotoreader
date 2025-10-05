from collections.abc import Generator
from typing import Any

import pytest
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
        driver="psycopg2",
    ) as container:
        # Wait for container to be ready
        container.get_connection_url()
        yield container


@pytest.fixture(scope="session")
def db_config(postgres_container: PgVectorContainer) -> dict[str, Any]:
    """Database configuration from testcontainer."""
    return {
        "host": postgres_container.get_container_host_ip(),
        "port": postgres_container.get_exposed_port(5432),
        "database": postgres_container.dbname,
        "username": postgres_container.username,
        "password": postgres_container.password,
        "url": postgres_container.get_connection_url(),
    }


@pytest.fixture(scope="session")
def postgres_client(db_config: dict[str, Any]) -> Generator[PostgresClient, None, None]:
    # Import and store original client
    import rotoreader.service

    original_client = rotoreader.service.PG_CLIENT

    client = None
    try:
        client = PostgresClient(db_url=db_config["url"])

        # Setup: Create pgvector extension and any initial schema
        with client.engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()

        # Monkey patch the global PG_CLIENT
        rotoreader.service.PG_CLIENT = client

        yield client

        # Teardown: Clean up tables
        with client.engine.connect() as conn:
            # Get all user tables and truncate them
            result = conn.execute(
                text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename NOT LIKE 'pg_%'
            """)
            )
            tables = [row[0] for row in result]

            if tables:
                # Disable foreign key checks, truncate, re-enable
                conn.execute(text("SET session_replication_role = replica"))
                for table in tables:
                    conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                conn.execute(text("SET session_replication_role = DEFAULT"))
                conn.commit()

    finally:
        # Restore original client
        rotoreader.service.PG_CLIENT = original_client
        if client:
            client.close()
