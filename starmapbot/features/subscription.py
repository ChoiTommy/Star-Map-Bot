'''
Syntax: /subscribe [starmap|astrodata|weather|iss|sun] [timings]
timings: time on a day, scheduled daily, UTC time for now

e.g. /subscribe weather,starmap,sun 20:00,22:30,12:00

without 2/1 arguments: show subscription information only

Database
"Subscription": {
    "user_id": {
        "chat_id": {
            "starmap": {"enabled": bool, "timing": {"hour": int, "minute": int}},
            "astrodata": {"enabled": bool, "timing": {"hour": int, "minute": int}},
            "weather": {"enabled": bool, "timing": {"hour": int, "minute": int}},
            "iss": {"enabled": bool, "timing": {"hour": int, "minute": int}},
            "sun": {"enabled": bool, "timing": {"hour": int, "minute": int}}
        }
    }
}

Syntax: /unsubscribe [starmap|astrodata|weather|iss|sun]
'''
from starmapbot.features.starmap import star_map_subscription
from starmapbot.features.astro_data import astro_data_subscription
from starmapbot.features.weather import weather_subscription
from starmapbot.features.iss import iss_subscription
from starmapbot.features.sun import sun_subscription
from datetime import time
from firebase_admin import db
from telegram import Update
from telegram.ext import CallbackContext

DEFAULT_FEATURES = {
    "starmap": star_map_subscription,
    "astrodata": astro_data_subscription,
    "weather": weather_subscription,
    "iss": iss_subscription,
    "sun": sun_subscription
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
        if int(timing[0]) not in range(24):
            return False, [], []
        if int(timing[1]) not in range(60):
            return False, [], []
        hour.append(int(timing[0]))
        minute.append(int(timing[1]))
    return True, hour, minute


def are_features_valid(li: list[str]) -> bool:
    for l in li:
        if l not in DEFAULT_FEATURES:
            return False
    return True


async def subscribe(update: Update, context: CallbackContext) -> None:

    # TODO check if user location exists

    args = context.args

    if len(args) == 2:
        f, t = context.args

        features = [f.lower() for f in f.split(',')]
        timings = t.split(',')

        if len(features) != len(timings):
            # number of features is not equal to number of timings
            await update.message.reply_text(text="The number of features must be equal to that of the timings. Please set again.")
            return

        if not are_features_valid(features):
            # some features are invalid
            await update.message.reply_text(text="Make sure the features are of the 5 only. Please set again.")
            return

        valid_time, hour, minute = are_timings_valid(timings)
        if not valid_time:
            # timings do not follow the format
            await update.message.reply_text(text="Please follow the format for timings `<hour:minute>`. Please set again.")
            return

    else:
        # not providing enough arguments
        await update.message.reply_text(text="Arguments missing. Please set again.")
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    ref = db.reference(f"/Subscriptions/{user_id}/{chat_id}")

    user_data = DEFAULT_DB # reset every time user set a new sub


    # add to user_data for pushing to the db & add to job queue
    for feature, h, m in zip(features, hour, minute):
        user_data[feature]["enabled"] = True
        user_data[feature]["timing"]["hour"] = h
        user_data[feature]["timing"]["minute"] = m

        t = time(hour=h, minute=m)
        context.job_queue.run_daily(
            callback = DEFAULT_FEATURES[feature],
            time = t,
            name = f"{user_id}_{chat_id}_{feature}",
            user_id = user_id,
            chat_id = chat_id
        )

    ref.set(user_data)


# async def unsubscribe(update: Update, context: CallbackContext) -> None:


def load_jobs_into_jobqueue(application): # during startup

    ref = db.reference(f"/Subscriptions")
    user_sub_data = ref.get()

    if user_sub_data is not None:
        for user_id, chat_info in user_sub_data.items():
            for chat_id, feature_info in chat_info.items():
                for feature_name, sub_info in feature_info.items():
                    if sub_info["enabled"]:
                        t = time(hour=sub_info["timing"]["hour"], minute=sub_info["timing"]["minute"])
                        application.job_queue.run_daily(
                            callback = DEFAULT_FEATURES[feature_name],
                            time = t,
                            name = f"{user_id}_{chat_id}_{feature_name}",
                            user_id = user_id,
                            chat_id = chat_id
                        )


def get_user_subscription_info(user_id, chat_id) -> dict:
    ref = db.reference(f"/Subscriptions/{user_id}/{chat_id}")
    return ref.get()