"""
helpers is a module that consists of all the helper functions used in this bot.

"""

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


def utcOffset_to_tzstring(offset=0) -> str:
    """This function generates a timezone string (e.g. UTC+9:00) from a UTC offset in integer.

    Args:
        offset (int): UTC offset in milliseconds

    Returns:
        str: Timezone string like 'UTC+9:00' or 'UTC-10:30'
    """

    offset /= 3600000 # 3600000 ms
    tz_hour = int(offset)
    tz_minutes = int((abs(offset) - abs(tz_hour)) * 60)
    if tz_hour >= 0:
        return f"UTC+{tz_hour}:{tz_minutes if tz_minutes>=10 else '0'+str(tz_minutes)}"
    else:
        return f"UTC{tz_hour}:{tz_minutes if tz_minutes>=10 else '0'+str(tz_minutes)}"