from collections import defaultdict

from pydantic import BaseModel, Field

from rotoreader.model.constants import NFLTeam


class FeedEntry(BaseModel):
    feed_id: str
    id: str
    title: str
    summary: str
    published: str
    link: str
    author: str = Field(default="Unknown")
    teams: list[NFLTeam] = []
    players: list[NFLTeam] = []


class FeedData(BaseModel):
    entries: list[FeedEntry] = Field(default_factory=list)
    _team_cache: dict[NFLTeam, list[FeedEntry]] = defaultdict(list)

    class Config:
        arbitrary_types_allowed = True

    def add_entry(self, entry: FeedEntry):
        if entry not in self.entries and isinstance(self.entries, list):
            self.entries.append(entry)  # pylint: disable=no-member
        if not entry.teams:
            print(f"Entry {entry.id} has no teams")
        for t in entry.teams:
            self._team_cache[t].append(entry)

    def get_entries_by_team(self, team: str) -> list[FeedEntry]:
        if team not in self._team_cache:
            return []
        return self._team_cache[team]
