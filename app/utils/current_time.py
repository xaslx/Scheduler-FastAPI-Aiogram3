from datetime import datetime

from .generate_time import moscow_tz


def current_time():
    return datetime.now(moscow_tz).replace(tzinfo=None)
