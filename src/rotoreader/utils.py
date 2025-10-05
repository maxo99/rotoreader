from datetime import UTC, datetime


def _get_utc_now():
    return datetime.now(UTC)
