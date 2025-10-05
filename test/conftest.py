from collections.abc import Generator

import pytest
from sqlalchemy import text

from rotoreader.adapters.postgres_client import PostgresClient
from rotoreader.config import POSTGRES_DB

TEARDOWN = True


@pytest.fixture(scope="function")
def fix_postgresclient() -> Generator[PostgresClient, None, None]:
    _client = PostgresClient()
    yield _client
    if TEARDOWN:
        with _client.engine.connect() as conn:
            conn.execute(
                text(
                    f"DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = '{POSTGRES_DB}') THEN TRUNCATE TABLE {POSTGRES_DB}, event CASCADE; END IF; END $$;"
                )
            )
            conn.commit()
    _client.close()
