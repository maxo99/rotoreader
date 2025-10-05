import logging

import feedparser

from rotoreader.constants import NEWS_RSS_FEEDS, NFLTeam
from rotoreader.model.feeddata import FeedData, FeedData

logger = logging.getLogger(__name__)


def collect_and_process_feeddata():
    fd = collect_feeddata()
    team_counts = process_feeddata(fd)
    return fd, team_counts


def collect_feeddatas() -> list[FeedData]:
    fd_list = []
    for feed_id, url in NEWS_RSS_FEEDS.items():
        logger.info(f"Fetching {feed_id} from {url}")
        feed = feedparser.parse(url)
        if feed.bozo:
            logger.error(f"Error fetching {feed_id}: {feed.bozo_exception}")
            continue

        for entry in feed.entries:
            if isinstance(entry, dict):
                logger.info(f"Processing {feed_id} entry {entry.get('id', '')}")
                try:
                    fd_list.add_entry(
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


def process_feeddata(fd_list: list[FeedData]):
    for fd in fd_list:
        for entry in fd.entries:
        entry.teams = [
            team
            for team in NFLTeam
            if any(name in entry.title for name in team.value)
            or any(name in entry.summary for name in team.value)
        ]

    team_counts = {team: len(entries) for team, entries in fd._team_cache.items()}
    for team, count in team_counts.items():
        logger.info(f"Team {team.name} has {count} entries")
    return team_counts


def preview_feed(feed_url, count=5):
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            raise ValueError(f"Error fetching feed: {feed.bozo_exception}")
        logger.info(f"Feed channel: {feed.channel}")
        for entry in feed.entries[:count]:
            logger.info(f"{entry.published}: {entry.title} ({entry.link})")
    except Exception as e:
        logger.error(f"Failed to process feed {feed_url}: {e}")
