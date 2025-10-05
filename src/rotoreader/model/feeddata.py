from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel

from rotoreader.utils import _get_utc_now


class FeedData(SQLModel):
    feed_id: str
    id: str = Field(sa_column=Column(String, primary_key=True, nullable=False))
    collected_at: datetime = Field(
        sa_column=Column(
            DateTime, primary_key=True, nullable=False, default=_get_utc_now
        ),
        default_factory=_get_utc_now,
    )
    title: str
    summary: str
    published: str
    link: str
    author: str = Field(default="Unknown")
    teams: list[str] = []
    players: list[str] = []


# class FeedsData(BaseModel):
#     entries: list[FeedData] = Field(default_factory=list)
#     _team_cache: dict[NFLTeam, list[FeedData]] = defaultdict(list)

#     class Config:
#         arbitrary_types_allowed = True

#     def add_entry(self, entry: FeedData):
#         if entry not in self.entries and isinstance(self.entries, list):
#             self.entries.append(entry)  # pylint: disable=no-member
#         if not entry.teams:
#             print(f"Entry {entry.id} has no teams")
#         for t in entry.teams:
#             self._team_cache[t].append(entry)

#     def get_entries_by_team(self, team: str) -> list[FeedData]:
#         if team not in self._team_cache:
#             return []
#         return self._team_cache[team]
