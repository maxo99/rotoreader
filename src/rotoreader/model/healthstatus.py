from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from rotoreader import __version__
from rotoreader.utils import _get_utc_now


class HealthStatusResponse(BaseModel):
    status: Literal["running"] = Field(default="running")
    timestamp: datetime = Field(default_factory=_get_utc_now)
    version: str | None = Field(default=__version__)
