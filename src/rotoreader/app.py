import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi_pagination import Page, Params, add_pagination
from fastapi_pagination.ext.sqlmodel import apaginate
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.ext.asyncio import AsyncSession

from rotoreader.config import APP_PORT, LOG_LEVEL
from rotoreader.model.collection import CollectionResponse
from rotoreader.model.feeddata import FeedData
from rotoreader.model.healthstatus import HealthStatusResponse
from rotoreader.service import PG_CLIENT
from rotoreader.service.feedsreader import (
    collect_and_process_feeddata,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""

    # Startup
    await PG_CLIENT.initialize()
    logging.info("PostgresClient initialized.")

    logging.info("Application startup complete.")
    yield
    logging.info("Application shutdown starting.")

    # Shutdown - cleanup if needed
    await PG_CLIENT.close()
    logging.info("PostgresClient connection closed.")
    
    logging.info("Application shutdown complete.")



app = FastAPI(lifespan=lifespan)
add_pagination(app)

# Setup Prometheus instrumentation (must be done before app starts)
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
logging.info("Prometheus metrics instrumentation configured.")


@app.get("/", response_model=HealthStatusResponse)
async def health():
    return HealthStatusResponse()


@app.put("/collect", response_model=CollectionResponse)
async def collect(
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


@app.get("/feed", response_model_exclude_none=True)
async def feeds(
    session: Annotated[AsyncSession, Depends(PG_CLIENT.get_session)],
    params: Annotated[Params, Depends()],
    team: Annotated[
        str | None,
        Query(
            description="Filter feeds by team abbreviation. If not provided, returns feeds for all teams."
        ),
    ] = None,
) -> Page[FeedData]:
    logger.info(f"Fetching feeds for team: {team} with params: {params}")
    query = PG_CLIENT.get_feeddatas_query(team)
    return await apaginate(session, query, params)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=APP_PORT, log_level=LOG_LEVEL)
