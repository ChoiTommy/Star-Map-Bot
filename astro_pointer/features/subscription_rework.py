"""
Ideas:

use ConversationHandler

Steps:
1. Ask for which features to subscribe to
2. Daily / Weekly / Monthly / Yearly ?
3. Ask for the date / time
4. Go back to step 2 for another subscription

Date/time picker

What if the user stops halfway through the process?

"""

from datetime import time, timedelta, timezone
from firebase_admin import db
from telegram import Update
from telegram.ext import CallbackContext
from tabulate import tabulate
from astro_pointer.features.starmap import star_map_subscription
from astro_pointer.features.astrodata import astro_data_subscription
from astro_pointer.features.weather import weather_subscription
from astro_pointer.features.iss import iss_subscription
from astro_pointer.features.sun import sun_subscription


DEFAULT_FEATURES = {
    "starmap": star_map_subscription,
    "astrodata": astro_data_subscription,
    "weather": weather_subscription,
    "sun": sun_subscription,
    "iss": iss_subscription
}


async def subscription_overview(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        text = "Your current subscriptions are:",
        reply_markup = subscription_keyboard()
    )