import logging

from rotoreader.service.teamprofiler import load_team_data

logger = logging.getLogger(__name__)


def test_team_population():
    teams = load_team_data()
    assert len(teams) > 0
