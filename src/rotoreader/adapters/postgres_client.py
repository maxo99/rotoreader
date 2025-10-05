import logging
from datetime import UTC, datetime

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

from rotoreader import config
from rotoreader.model.feeddata import FeedData

# from oddstracker.domain.kambi_event import Event, SQLModel

logger = logging.getLogger(__name__)


# @dataclass
# class SimilarityResponse:
#     events: list[Event]
#     scores: list[float]


class PostgresClient:
    def __init__(self, db_url: str | None = None):
        try:
            logger.info("Initializing Postgres client")
            self.db_url = db_url or config.get_pg_url()
            self.engine = create_engine(self.db_url)
            self.session_maker = sessionmaker(bind=self.engine)
            self._session = self.session_maker()

            with self.engine.connect() as conn:
                # conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()

            self._create_tables()
        except Exception as e:
            logger.error(f"Error initializing Postgres client: {e}")
            raise e

    def _create_tables(self):
        if "event" not in inspect(self.engine).get_table_names():
            logger.info("Creating Postgres tables if they do not exist")
            SQLModel.metadata.create_all(self.engine)
            logger.info("Postgres tables created/checked successfully")
        else:
            logger.warning(
                f"SQL tables already exist: {list(SQLModel.metadata.tables.keys())}"
            )

    def validate_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Postgres connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"Error validating Postgres connection: {e}")
            return False

    def close(self):
        try:
            self._session.close()
            self.engine.dispose()
            logger.info("Closed Postgres client connection")
        except Exception as e:
            logger.error(f"Error closing Postgres client connection: {e}")
            raise e

    def add_feeddata(self, feeddata: FeedData):
        try:
            logger.info(f"Upserting feeddata {feeddata.id}.")
            with self.session_maker() as session:
                session.add(feeddata)
                session.commit()
                logger.info(f"Upserted feeddata {feeddata.id} successfully.")
        except Exception as e:
            logger.error(f"Error upserting feeddata: {e}")
            raise e

    # def get_events(self, include_deleted: bool = False, **filters) -> list[KambiEvent]:
    #     try:
    #         logger.info(f"Fetching events from with {filters}")
    #         with self.session_maker() as session:
    #             query = select(KambiEvent)

    #             if not include_deleted:
    #                 query = query.where(KambiEvent.deleted_at == None)

    #             if filters:
    #                 for key, value in filters.items():
    #                     if key.startswith("not_"):
    #                         actual_key = key[4:]
    #                         query = query.where(
    #                             getattr(KambiEvent, actual_key) != value
    #                         )
    #                     else:
    #                         query = query.where(getattr(KambiEvent, key) == value)
    #             return list(session.execute(query).scalars().all())
    #     except Exception as e:
    #         logger.error(f"Error getting events: {e}")
    #         raise e

    # def get_event(self, event_id: int) -> KambiEvent | None:
    #     try:
    #         logger.info(f"Fetching event with ID {event_id}")
    #         with self.session_maker() as session:
    #             event = session.get(KambiEvent, event_id)
    #             return event
    #     except Exception as e:
    #         logger.error(f"Error getting events: {e}")
    #         raise e

    # def get_bet_offers_for_event(self, event_id: int, offer: str | None = None) -> list[BetOffer]:
    #     try:
    #         logger.info(f"Fetching bet offers for event ID {event_id}")
    #         with self.session_maker() as session:
    #             query = select(BetOffer).where(BetOffer.eventId == event_id)
    #             if offer:
    #                 query = query.where(BetOffer.betOfferType == offer)
    #             bet_offers = list(session.execute(query).scalars().all())
    #             return bet_offers
    #     except Exception as e:
    #         logger.error(f"Error getting bet offers for event {event_id}: {e}")
    #         raise e

    # def get_bet_offer_history(self, bet_offer_id: int, event_id: int, limit: int = 2) -> list[BetOffer]:
    #     try:
    #         logger.debug(f"Fetching history for bet offer {bet_offer_id}")
    #         with self.session_maker() as session:
    #             result = session.execute(
    #                 text(
    #                     'SELECT * FROM betoffer WHERE id = :bet_offer_id AND "eventId" = :event_id '
    #                     "ORDER BY collected_at DESC LIMIT :limit"
    #                 ),
    #                 {"bet_offer_id": bet_offer_id, "event_id": event_id, "limit": limit}
    #             )
    #             rows = result.fetchall()
    #             bet_offers = []
    #             for row in rows:
    #                 bet_offer = BetOffer(**dict(row._mapping))
    #                 bet_offers.append(bet_offer)
    #             return bet_offers
    #     except Exception as e:
    #         logger.error(f"Error getting bet offer history: {e}")
    #         raise e
