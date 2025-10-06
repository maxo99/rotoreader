import nfl_data_py as nfl

from rotoreader.model.teamdata import TeamData
from rotoreader.service import PG_CLIENT


def load_team_data():
    teams = nfl.import_team_desc()
    return [TeamData.from_nfl_data(row) for _, row in teams.iterrows()]


async def load_and_store_team_data():
    teams_data = load_team_data()
    await PG_CLIENT.add_teamdata(teams_data)


TEAMS_PRELOADED = False
TEAMS_CACHE: list[TeamData] | None = None


async def get_teams() -> list[TeamData]:
    global TEAMS_PRELOADED, TEAMS_CACHE
    if not TEAMS_PRELOADED:
        await load_and_store_team_data()
        TEAMS_PRELOADED = True
    if TEAMS_CACHE is None:
        TEAMS_CACHE = await PG_CLIENT.get_teams()
    return TEAMS_CACHE
