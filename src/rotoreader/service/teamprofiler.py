from functools import lru_cache

import nfl_data_py as nfl

from rotoreader.model.teamdata import TeamData
from rotoreader.service import PG_CLIENT


def load_team_data():
    teams = nfl.import_team_desc()
    return [TeamData.from_nfl_data(row) for _, row in teams.iterrows()]


def load_and_store_team_data():
    teams_data = load_team_data()
    PG_CLIENT.add_teamdata(teams_data)



TEAMS_PRELOADED = False

@lru_cache(maxsize=1)
def get_teams() -> list[TeamData]:
    global TEAMS_PRELOADED
    if not TEAMS_PRELOADED:
        load_and_store_team_data()
        TEAMS_PRELOADED = True
    return PG_CLIENT.get_teams()
