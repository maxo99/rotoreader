import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel, select

from rotoreader import config
from rotoreader.model.feeddata import FeedData
from rotoreader.model.teamdata import TeamData

logger = logging.getLogger(__name__)


class PostgresClient:
    def __init__(self, db_url: str | None = None, use_null_pool: bool = False):
        try:
            logger.info("Initializing Postgres client")
            self.db_url = db_url or config.get_pg_url()
            if self.db_url.startswith("postgresql://"):
                self.db_url = self.db_url.replace(
                    "postgresql://", "postgresql+asyncpg://", 1
                )

            engine_kwargs = {"poolclass": NullPool} if use_null_pool else {}
            self.engine = create_async_engine(self.db_url, **engine_kwargs)
            self.session_maker = async_sessionmaker(
                bind=self.engine, class_=AsyncSession, expire_on_commit=False
            )
        except Exception as e:
            logger.error(f"Error initializing Postgres client: {e}")
            raise e

    async def get_session(self):
        """Dependency to get database session. Use with FastAPI Depends."""
        async with self.session_maker() as session:
            yield session

    async def initialize(self):
        """Initialize database tables. Call this after creating the client."""
        await self._create_tables()

    async def _create_tables(self):
        """Create tables if they don't exist"""
        try:
            async with self.engine.begin() as conn:
                # await conn.run_sync(lambda sync_conn: sync_conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector")))
                await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Postgres tables created/checked successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise e

    async def validate_connection(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Postgres connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"Error validating Postgres connection: {e}")
            return False

    async def close(self):
        try:
            await self.engine.dispose()
            logger.info("Closed Postgres client connection")
        except Exception as e:
            logger.error(f"Error closing Postgres client connection: {e}")
            raise e

    async def add_feeddata(self, feeddata: FeedData):
        try:
            logger.info(f"Upserting feeddata {feeddata.id}.")
            async with self.session_maker() as session:
                session.add(feeddata)
                await session.commit()
                logger.info(f"Upserted feeddata {feeddata.id} successfully.")
        except Exception as e:
            logger.error(f"Error upserting feeddata: {e}")
            raise e

    async def get_all_feeddatas(self) -> list[FeedData]:
        try:
            logger.info("Fetching all feeddata from DB")
            async with self.session_maker() as session:
                query = select(FeedData)
                result = await session.execute(query)
                feeddatas = list(result.scalars().all())
                return feeddatas
        except Exception as e:
            logger.error(f"Error getting feeddata: {e}")
            raise e

    async def get_feeds_for_team(self, team_abbr: str) -> list[FeedData]:
        try:
            logger.info(f"Fetching feeddata for team {team_abbr}")
            async with self.session_maker() as session:
                query = select(FeedData).where(
                    text(f"teams::jsonb @> '[\"{team_abbr}\"]'::jsonb")
                )
                result = await session.execute(query)
                feeddatas = list(result.scalars().all())
                return feeddatas
        except Exception as e:
            logger.error(f"Error getting feeddata for team {team_abbr}: {e}")
            raise e

    def get_feeddatas_query(self, team_abbr: str | None = None):
        """Return a SQLModel query for pagination. Does not execute the query."""
        if team_abbr:
            return select(FeedData).where(
                text(f"teams::jsonb @> '[\"{team_abbr}\"]'::jsonb")
            )
        return select(FeedData)

    async def add_teamdata(self, teamdata: list[TeamData]):
        try:
            logger.info(f"Upserting teamdata {len(teamdata)}.")
            async with self.session_maker() as session:
                # if none exist add all
                result = await session.execute(select(TeamData).limit(1))
                if not result.first():
                    session.add_all(teamdata)
                    await session.commit()
                    logger.info(
                        f"Upserted teamdata {[td.team_id for td in teamdata]} successfully."
                    )
        except Exception as e:
            logger.error(f"Error upserting teamdata: {e}")
            raise e

    async def get_teams(self) -> list[TeamData]:
        try:
            logger.info("Fetching all teams from DB")
            async with self.session_maker() as session:
                query = select(TeamData)
                result = await session.execute(query)
                teams = list(result.scalars().all())
                return teams
        except Exception as e:
            logger.error(f"Error getting teams: {e}")
            raise e

    async def get_team_by_abbr(self, team_abbr: str) -> TeamData | None:
        try:
            logger.info(f"Fetching team with abbreviation {team_abbr}")
            async with self.session_maker() as session:
                team = await session.get(TeamData, team_abbr)
                return team
        except Exception as e:
            logger.error(f"Error getting team by abbreviation: {e}")
            raise e
