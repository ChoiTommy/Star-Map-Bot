"""
A module handling user subscriptions of daily notifications

Usage: /sub(scribe) [starmap|astrodata|weather|iss|sun] [timings]
timings:
    schedule every day, separated by commas
    one subscription per feature, old sub timings will be replaced by the new one
Example: /sub astrodata,sun 22:00,12:00

Usage: /unsub(scribe) [starmap|astrodata|weather|iss|sun]
Example: /unsub starmap,astrodata,weather,iss,sun
"""

from astro_pointer.features.starmap import star_map_subscription
from astro_pointer.features.astrodata import astro_data_subscription
from astro_pointer.features.weather import weather_subscription
from astro_pointer.features.iss import iss_subscription
from astro_pointer.features.sun import sun_subscription
from datetime import time, timedelta, timezone
from firebase_admin import db
from telegram import Update
from telegram.ext import CallbackContext
from tabulate import tabulate


DEFAULT_FEATURES = {
    "starmap": star_map_subscription,
    "astrodata": astro_data_subscription,
    "weather": weather_subscription,
    "sun": sun_subscription,
    "iss": iss_subscription
}


def are_timings_valid(timings_list: list[str]) -> (bool, list[str], list[str]):
    """Check the format and the ranges of the timing inputs

    Args:
        timing_list (list[str]): a list of time strings like ['1:20', '14:30', '18:00']

    Returns:
        bool: True if all timings are valid
        list[str]: a list of hour strings like ['01', '14', '18'] if valid
        list[str]: a list of minute strings like ['20', '30', '00'] if valid
    """

    hour, minute = [], []
    for hours_n_minutes in timings_list:
        timing = [time for time in hours_n_minutes.split(':')]
        if not (timing[0].isdigit() and timing[1].isdigit()):
            return False, [], []
        if (len(timing) != 2) or not (int(timing[0]) in range(24) and (int(timing[1]) in range(60))):
            return False, [], []
        hour.append(f"{int(timing[0]):02d}")
        minute.append(f"{int(timing[1]):02d}")
    return True, hour, minute


def are_features_valid(features_list: list[str]) -> bool:
    """Check if the feature inputs are valid

    Args:
        features_list (list[str]): a list of features that users would like to subscribe

    Returns:
        bool: True if all fall into the 5 presets [starmap|astrodata|weather|iss|sun]
    """

    for feature in features_list:
        if feature not in DEFAULT_FEATURES:
            return False
    return True


async def subscribe(update: Update, context: CallbackContext) -> None:
    """Handle subscription requests. Possible improvements: cleaner input error handling"""

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    DEFAULT_DB = {
        key: {
            "enabled": False,
            "timing": {
                "hour": "-1",
                "minute": "-1"
            }
        }
        for key in DEFAULT_FEATURES
    }

    args = context.args

    if len(args) == 2:
        f, t = context.args

        features = [f.lower() for f in f.split(',')]
        timings = t.split(',')

        if len(features) != len(timings):
            # number of features is not equal to number of timings
            await update.message.reply_markdown_v2(
                text = ("The number of features must be equal to that of the timings\. Please try again\. \n"
                        "e\.g\. `/sub astrodata,sun 22:00,12:00`")
            )
            return

        if not are_features_valid(features):
            # some features are invalid
            await update.message.reply_markdown_v2(
                text = ("Make sure the features are of the 5 presets only: `starmap|astrodata|weather|sun|iss` \n"
                        "Please try again\.")
            )
            return

        valid_time, hour, minute = are_timings_valid(timings)
        if not valid_time:
            # timings do not follow the format
            await update.message.reply_markdown_v2(
                text = "Please put the timings in the format of `hour:minute` \(24\-hr\) "
            )
            return

    else:
        # not providing enough arguments
        tble = get_user_subscription_info(user_id, chat_id)
        await update.message.reply_markdown_v2(
            text = ("Arguments missing\. \n"
                    "Syntax: `/sub [starmap|astrodata|weather|iss|sun] [timings]` \n"
                    "Separate features/timings with commas \n"
                    "e\.g\. `/sub astrodata,sun 22:00,12:00` \n\n"

                    "Here are your current subscriptions: \n"
                    f"`{tabulate(tble, tablefmt='fancy_grid', headers=['Subs', 'Daily Time'])}`")
        )
        return

    ref = db.reference(f"/Users/{user_id}")
    utcOffset = ref.get()["utcOffset"] if ref.get() is not None else 0

    ref = db.reference(f"/Subscriptions/{user_id}/{chat_id}")
    user_data = DEFAULT_DB if ref.get() is None else ref.get()

    display_text = []

    # add to user_data for pushing to the db & add to job queue
    for feature, h, m in zip(features, hour, minute):
        if user_data[feature]["enabled"]:
            jobs_list = context.job_queue.get_jobs_by_name(f"{user_id}_{chat_id}_{feature}")
            for job in jobs_list:
                job.schedule_removal()
            display_text.append([feature, f"{user_data[feature]['timing']['hour']}:{user_data[feature]['timing']['minute']} -> {h}:{m}"])
        else:
            display_text.append([feature, f"{h}:{m}"])

        t = time(
            hour = int(h),
            minute = int(m),
            tzinfo = timezone(offset=timedelta(seconds=utcOffset))
        )        # Time in accordance with user's timezone set with /setlocation

        user_data[feature]["enabled"] = True
        user_data[feature]["timing"]["hour"] = h    # Store the raw timing provided by users
        user_data[feature]["timing"]["minute"] = m

        context.job_queue.run_daily(
            callback = DEFAULT_FEATURES[feature],
            time = t,
            name = f"{user_id}_{chat_id}_{feature}",
            user_id = user_id,
            chat_id = chat_id
        )

    ref.update(user_data)

    await update.message.reply_markdown_v2(
        text = (f'Congrats {update.effective_user.mention_markdown_v2()}, \n'
                "Your newly subscribed/modified subscriptions: \n"
                f"`{tabulate(display_text, tablefmt='fancy_grid', headers=['Subs', 'Daily Time'])}`")
    )


async def unsubscribe(update: Update, context: CallbackContext) -> None:
    """Handle unsubscribing requests"""

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    ref = db.reference(f"/Subscriptions/{user_id}/{chat_id}")

    if ref.get() is None:
        await update.message.reply_text(text="You have yet to subscribe to any features. Nothing has been unsubscribed.")

    else:
        user_data = ref.get()
        args = context.args

        if len(args) == 1:
            f = context.args[0]
            features = [f.lower() for f in f.split(',')]

            if not are_features_valid(features):
                # some features are invalid
                await update.message.reply_text(
                    text = ("Make sure the features are of the 5 presets only: `starmap|astrodata|weather|sun|iss` \n"
                            "Please try again\.")
                )
                return

        else:
            # not providing enough arguments
            await update.message.reply_markdown_v2(
                text = ("Arguments missing\. \n"
                        "Syntax: `/unsub [starmap|astrodata|weather|iss|sun]` \n"
                        "Separate multiple features with commas\. \n"
                        "e\.g\. `/unsub starmap,weather,astrodata,iss,sun`")
            )
            return

        display_text = []

        for feature in features:
            if user_data[feature]["enabled"]:
                jobs_list = context.job_queue.get_jobs_by_name(f"{user_id}_{chat_id}_{feature}")
                for job in jobs_list:
                    job.schedule_removal()

                user_data[feature]["enabled"] = False
                user_data[feature]["timing"]["hour"] = "-1"
                user_data[feature]["timing"]["minute"] = "-1"
                display_text.append([f"{feature}"])
            else:
                display_text.append([f"{feature} (disabled already)"])

        if count_no_of_subs(user_data) == 0:
            ref.set({})     # deletion
        else:
            ref.update(user_data)

        await update.message.reply_markdown_v2(
            text = ("You have been successfully unsubscribed from \n"
                    f"`{tabulate(display_text, tablefmt='fancy_grid', headers=['Removed subscriptions'])}`")
        )


async def load_jobs_into_jobqueue(context: CallbackContext) -> None:
    """Load subscriptions into jobqueue while starting up the bot"""

    ref = db.reference(f"/Subscriptions")
    user_sub_data = ref.get()

    if user_sub_data is not None:
        for user_id, chat_info in user_sub_data.items():
            for chat_id, feature_info in chat_info.items():
                for feature_name, sub_info in feature_info.items():
                    if sub_info["enabled"]:
                        ref = db.reference(f"/Users/{user_id}")
                        utcOffset = ref.get()["utcOffset"]

                        t = time(
                            hour = int(sub_info["timing"]["hour"]),
                            minute = int(sub_info["timing"]["minute"]),
                            tzinfo = timezone(offset=timedelta(seconds=utcOffset))
                        )

                        context.job_queue.run_daily(
                            callback = DEFAULT_FEATURES[feature_name],
                            time = t,
                            name = f"{user_id}_{chat_id}_{feature_name}",
                            user_id = user_id,
                            chat_id = chat_id
                        )


def get_user_subscription_info(user_id, chat_id) -> list[list[str]]:
    """Get user subscription information

    Args:
        user_id (int): Telegram user ID
        chat_id (int): Telegram chat ID (same as user_id if the chat is a DM to the bot)

    Returns:
        list[list[str]]: a complicated thing to generate a beautiful table with `tabulate.tabulate`
    """

    DEFAULT_DB = {
        key: {
            "enabled": False,
            "timing": {
                "hour": "-1",
                "minute": "-1"
            }
        }
        for key in DEFAULT_FEATURES
    }
    ref = db.reference(f"/Subscriptions/{user_id}/{chat_id}")
    display_text = []
    user_data = ref.get() if ref.get() is not None else DEFAULT_DB
    for feature, info in user_data.items():
        if info["enabled"]:
            display_text.append([feature, f"{info['timing']['hour']}:{info['timing']['minute']}"])
        else:
            display_text.append([feature, "Not subscribed"])

    return display_text


def count_no_of_subs(user_data) -> int:
    """Count the number of active subscriptions of a user

    Args:
        user_data (dict): user subscription dict

    Returns:
        int: number of active subscriptions
    """

    n = 0
    for item in user_data.values():
        if item["enabled"]:
            n += 1
    return n
