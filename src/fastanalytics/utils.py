from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """Get the current datetime aware of UTC timezone
    :return: `datetime` object with UTC timezone"""
    return datetime.now(timezone.utc).replace(tzinfo=timezone.utc)
