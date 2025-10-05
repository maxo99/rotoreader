import logging

from sqlalchemy import text

from rotoreader.adapters.postgres_client import PostgresClient
from rotoreader.service.feedsreader import collect_and_process_feeddata, get_feeddatas
from rotoreader.service.teamprofiler import (
    get_teams,
    load_and_store_team_data,
    load_team_data,
)

logger = logging.getLogger(__name__)


def test_connection(postgres_client: PostgresClient):
    try:
        postgres_client.validate_connection()
        print("Connection successful.")
    except Exception as e:
        # fix_postgresclient.client.info()
        print("PostgreSQL connection failed:", e)
        raise e


def test_pgvector_extension_available(postgres_client: PostgresClient):
    with postgres_client.engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT extname FROM pg_extension WHERE extname = 'vector'
        """)
        )
        extensions = [row[0] for row in result]
        assert "vector" in extensions


def test_team_population(postgres_client: PostgresClient):
    load_and_store_team_data()
    assert len(get_teams()) == 36


def test_get_team_by_abbr(postgres_client: PostgresClient):
    teams_data = load_team_data()
    postgres_client.add_teamdata(teams_data)
    team = postgres_client.get_team_by_abbr("MIA")
    assert team is not None
    assert team.team_abbr == "MIA"


def test_feeds_store_get(postgres_client):
    collect_and_process_feeddata()
    retrieved = get_feeddatas()
    assert len(retrieved) > 0
    test_team = None
    i = 0
    while not test_team:
        if retrieved[i].teams:
            test_team = retrieved[i].teams[0]
        i += 1
    assert test_team in [team.team_abbr for team in get_teams()]
    team_feeddata = get_feeddatas(test_team)
    assert len(team_feeddata) > 0
