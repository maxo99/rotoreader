import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi_pagination import Page, Params, add_pagination
from fastapi_pagination.ext.sqlmodel import apaginate
from sqlalchemy.ext.asyncio import AsyncSession

from rotoreader import __version__, utils
from rotoreader.app_initializer import (
    instrument_prometheus,
    instrument_tracing,
    setup_tracing,
)
from rotoreader.config import APP_PORT, LOG_LEVEL
from rotoreader.model.collection import CollectionResponse
from rotoreader.model.feeddata import FeedData
from rotoreader.model.healthstatus import HealthStatusResponse
from rotoreader.service import get_client
from rotoreader.service.feedsreader import collect_and_process_feeddata

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info(f"Application startup starting with app:{app.version}.")


    await get_client().initialize()
    logging.info("PostgresClient initialized.")
    logging.info("Application startup complete.")
    yield

    logging.info("Application shutdown starting.")
    await get_client().close()
    logging.info("Application shutdown complete.")


START_UP = utils._get_utc_now()
logger.info(f"Application version:{__version__} startup time (UTC): {START_UP}")

setup_tracing()
app = FastAPI(
    lifespan=lifespan,
    version=__version__,
)
add_pagination(app)
instrument_tracing(app)
instrument_prometheus(app)


@app.get("/", response_model=HealthStatusResponse, operation_id="health_check")
async def health():
    return HealthStatusResponse(startup_time=START_UP)


@app.put(
    "/collect",
    response_model=CollectionResponse,
    tags=["feeds"],
    operation_id="collect_feeddata",
    summary="Collect feed data from RSS feeds",
)
async def collect_feeddata(
    limit: Annotated[
        int,
        Query(description="Limit to pull"),
    ] = 5,
    provider: Annotated[
        str | None,
        Query(description="Provider to pull from."),
    ] = None,
):
    count = await collect_and_process_feeddata(limit=limit)
    return CollectionResponse(count=count)


@app.get(
    "/feed",
    response_model_exclude_none=True,
    tags=["feeds"],
    operation_id="get_feeds",
    summary="Get feed data, optionally filtered by team",
)
async def get_feeds(
    session: Annotated[AsyncSession, Depends(get_client().get_session)],
    params: Annotated[Params, Depends()],
    team: Annotated[
        str | None,
        Query(
            description="Filter feeds by team abbreviation. If not provided, returns feeds for all teams."
        ),
    ] = None,
) -> Page[FeedData]:
    logger.info(f"Fetching feeds for team: {team} with params: {params}")
    query = get_client().get_feeddatas_query(team)
    return await apaginate(session, query, params)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=APP_PORT, log_level=LOG_LEVEL)
