'''
Syntax: /subscribe [starmap|astrodata|weather|iss|sun] [timings]
timings: time on a day, scheduled daily, UTC time for now

e.g. /subscribe weather,starmap,sun 20:00,22:30,12:00

without 2/1 arguments: show subscription information only

Database
"Subscription": {
        "user_id": {
            "starmap": {"enabled": bool, "time": str},
            "astrodata": {"enabled": bool, "time": str},
            "weather": {"enabled": bool, "time": str},
            "iss": {"enabled": bool, "time": str},
            "sun": {"enabled": bool, "time": str},
        }, ...
}

Syntax: /unsubscribe [starmap|astrodata|weather|iss|sun]
'''
from starmap import send_star_map
from astrodata import show_astro_data
from weather import show_weather_data
from iss import iss_live_location
from sun import send_sun_photo

from datetime import time
from firebase_admin import db
from telegram import Update
from telegram.ext import CallbackContext

DEFAULT_FEATURES = {
    "starmap": send_star_map,
    "astrodata": show_astro_data,
    "weather": show_weather_data,
    "iss": iss_live_location,
    "sun": send_sun_photo
}

DEFAULT_DB = {
            "starmap": {"enabled": False, "timing": {"hour": 0, "minute": 0}},
            "astrodata": {"enabled": False, "timing": {"hour": 0, "minute": 0}},
            "weather": {"enabled": False, "timing": {"hour": 0, "minute": 0}},
            "iss": {"enabled": False, "timing": {"hour": 0, "minute": 0}},
            "sun": {"enabled": False, "timing": {"hour": 0, "minute": 0}},
}


def are_timings_valid(li: list[str]) -> (bool, list[int], list[int]):
    # check colon, check ranges
    hour, minute = [], []
    for l in li:
        timing = l.split(':')
        if len(timing) != 2:
            return False, [], []
        if int(timing[0]) not in range(25):
            return False, [], []
        if int(timing[1]) not in range(60):
            return False, [], []
        hour.append(timing[0])
        minute.append(timing[1])
    return True, hour, minute


def are_features_valid(li: List[str]) -> bool:
    for l in li:
        if l not in DEFAULT_FEATURES:
            return False
    return True


async def subscribe(update: Update, context: CallbackContext) -> None:

    f, t = context.args[0], context.args[1]

    if f is not None and t is not None:
        features = [f.lower() for f in f.split(',')]
        timings = t.split(',')

        if len(features) != len(timings):
            # number of features is not equal to number of timings
            update.message.reply_markdown_v2(text="The number of features must be equal to that of the timings. Please set again.")
            return

        valid_time, hour, minute = are_timings_valid(timings)
        if not valid_time:
            # timings do not follow the format
            update.message.reply_markdown_v2(text="Please follow the format for timings `<hour:minute>`. Please set again.")
            return

        if not are_features_valid(features):
            # some features are invalid
            update.message.reply_markdown_v2(text="Make sure the features are of the 5 only. Please set again.")
            return

    else:
        # not providing enough arguments
        update.message.reply_markdown_v2(text="Arguments missing. Please set again.")
        return

    user_id = str(update.effective_user.id)
    ref = db.reference(f"/Subscriptions/{user_id}")

    user_data = DEFAULT_DB # reset every time user set a new sub


    # add to user_data for pushing to the db & add to job queue
    for i in range(len(features)):
        user_data[features[i]]["enabled"] = True
        user_data[features[i]]["timing"]["hour"] = hour[i]
        user_data[features[i]]["timing"]["minute"] = minute[i]

        time = time(hour=hour[i], minute=minute[i])
        context.job_queue.run_daily(DEFAULT_FEATURES[features[i]], time=time, name=f"{user_id}_{features[i]}")

    ref.set(user_data)


# async def unsubscribe(update: Update, context: CallbackContext) -> None: