"""
A module consists of all the helper functions used in this bot

"""

import time
from datetime import datetime
from pytz import timezone, utc
from timezonefinder import TimezoneFinder


tf = TimezoneFinder()


def get_offset(lat=0, longi=0) -> float:
    """Returns a location's timezone offset from UTC in seconds.

    Args:
        lat (float): Latitude of a point.
        longi (float): Longitude of a point.

    Returns:
        float: Timezone offset from UTC in seconds.
    """

    today = datetime.now()
    tz_target = timezone(tf.certain_timezone_at(lng=longi, lat=lat))
    # ATTENTION: tz_target could be None! handle error case
    today_target = tz_target.localize(today)
    today_utc = utc.localize(today)
    return (today_utc - today_target).total_seconds()


def utc_offset_to_tzstring(offset=0) -> str:
    """This function generates a timezone string (e.g. UTC+9:00) from a UTC offset in integer.
        Deprecated. Use `timezone(offset=timedelta(seconds=offset)).tzname(None)` instead.

    Args:
        offset (int): UTC offset in seconds

    Returns:
        str: Timezone string like 'UTC+9:00' or 'UTC-10:30'
    """

    offset /= 3600 # 3600000 ms
    tz_hour = int(offset)
    tz_minutes = int((abs(offset) - abs(tz_hour)) * 60)
    if tz_hour >= 0:
        return f"UTC+{tz_hour:02d}:{tz_minutes:02d}"

    return f"UTC{tz_hour:03d}:{tz_minutes:02d}"


def get_current_date_time_string(utc_offset=0) -> str:
    """Get a string of current date and time. e.g. 2022-05-26 00:00:00. Default is UTC time.

    Args:
        utc_offset (int): UTC offset in seconds

    Returns:
        str: a string consisting of date and time
    """
    current_timestamp = int(time.time()) # in UTC
    return str(datetime.utcfromtimestamp(current_timestamp + utc_offset))
