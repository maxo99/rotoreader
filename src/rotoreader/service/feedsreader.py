import logging

import feedparser

from rotoreader.constants import NEWS_RSS_FEEDS
from rotoreader.model.feeddata import FeedData
from rotoreader.service import PG_CLIENT
from rotoreader.service.teamprofiler import get_teams

logger = logging.getLogger(__name__)


FEED_FETCH_LIMIT = 5


async def collect_and_process_feeddata() -> int:
    fd = await collect_feeddatas()
    await process_feeddata(fd)
    return len(fd)


async def collect_feeddatas() -> list[FeedData]:
    fd_list = []
    for feed_id, url in NEWS_RSS_FEEDS.items():
        logger.info(f"Fetching {feed_id} from {url}")
        feed = feedparser.parse(url)
        if feed.bozo:
            logger.error(f"Error fetching {feed_id}: {feed.bozo_exception}")
            continue

        for entry in feed.entries[:FEED_FETCH_LIMIT]:
            if isinstance(entry, dict):
                logger.info(f"Processing {feed_id} entry {entry.get('id', '')}")
                try:
                    fd_list.append(
                        FeedData(
                            feed_id=feed_id,
                            id=str(entry.get("id", "")),
                            title=str(entry.get("title", "")),
                            summary=str(entry.get("summary", "")),
                            published=str(entry.get("published", "")),
                            author=str(entry.get("author", "Unknown")),
                            link=str(entry.get("link", "")),
                        )
                    )
                except Exception as e:
                    logger.error(f"Error processing {feed_id} entry {entry}: {e}")
                    continue
                logger.debug(entry)
        logger.info(f"Collected {len(fd_list)} entries from {feed_id}")
    return fd_list


async def process_feeddata(fd_list: list[FeedData]):
    for fd in fd_list:
        logger.info(f"Processing feed data {fd.id}")
        try:
            teams = await get_teams()
            for team in teams:
                if any(tag in fd.title for tag in team.searchTags) or any(
                    name in fd.summary for name in team.searchTags
                ):
                    logger.info(f"Matched team {team.team_abbr} for feed {fd.id}")
                    fd.teams.append(team.team_abbr)
                    if len(fd.teams) >= 2:
                        break
            logger.info(f"Storing feed data {fd.id} with teams {fd.teams}")
            await PG_CLIENT.add_feeddata(fd)
        except Exception as e:
            logger.error(f"Error processing feed data {fd.id}: {e}")


async def get_feeddatas(team_abbr: str | None = None) -> list[FeedData]:
    if team_abbr:
        return await PG_CLIENT.get_feeds_for_team(team_abbr)
    return await PG_CLIENT.get_all_feeddatas()
