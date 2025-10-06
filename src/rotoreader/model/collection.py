from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from rotoreader import __version__
from rotoreader.utils import _get_utc_now


class CollectionResponse(BaseModel):
    count: int = Field(default=0)
    status: Literal["completed", "failed"] = Field(default="completed")
    timestamp: datetime = Field(default_factory=_get_utc_now)
    version: str | None = Field(default=__version__)
