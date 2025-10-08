from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String
from sqlmodel import Field, SQLModel

from rotoreader.utils import _get_utc_now


class FeedData(SQLModel, table=True):
    feed_id: str
    id: str = Field(sa_column=Column(String, primary_key=True, nullable=False))
    collected_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            primary_key=True,
            nullable=False,
            default=_get_utc_now,
        ),
        default_factory=_get_utc_now,
    )
    title: str
    summary: str
    published: str
    link: str
    author: str = Field(default="Unknown")
    teams: list[str] = Field(default=[], sa_column=Column(JSON))
    players: list[str] = Field(default=[], sa_column=Column(JSON))

    @classmethod
    def from_feedparserdict(cls, feed_id: str, data: dict) -> "FeedData":
        return cls(
            feed_id=feed_id,
            id=str(data.get("id", "")),
            title=str(data.get("title", "")),
            summary=str(data.get("summary", "")),
            published=str(data.get("published", "")),
            author=str(data.get("author", "Unknown")),
            link=str(data.get("link", "")),
            teams=[],
            players=[],
            collected_at=_get_utc_now(),
        )
