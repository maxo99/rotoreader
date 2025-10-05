import logging

from rotoreader.model.feeddata import FeedData

logger = logging.getLogger(__name__)


def test_connection(fix_postgresclient):
    try:
        fix_postgresclient.validate_connection()
        print("Connection successful.")
    except Exception as e:
        # fix_postgresclient.client.info()
        print("PostgreSQL connection failed:", e)
        raise e


def test_event_store_retrieve(sample_data, fix_postgresclient):
    TEST_LIMIT = 5
    sample_data = sample_data[:TEST_LIMIT]
    for i, e in enumerate(sample_data):
        logger.info(f"Adding feeddata:{i} {e['feeddata']['id']}")
        try:
            feeddata = FeedData(**e['feeddata'])
            fix_postgresclient.add_feeddata(feeddata)
        except Exception as ex:
            logger.error(f"Failed to parse feeddata: {e['feeddata']['id']}, error: {ex}")
            raise ex
    for i, e in enumerate(sample_data):
        logger.info(f"Retrieving feeddata:{i} {e['feeddata']['id']}")
        retrieved = fix_postgresclient.get_feeddata(e["feeddata"]["id"])
        assert retrieved is not None
    assert True
