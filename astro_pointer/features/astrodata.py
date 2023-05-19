"""
This file consists of functions fetching and displaying astronomical data.

"""

import requests
from firebase_admin import db
from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from tabulate import tabulate
from astro_pointer.helpers import get_current_date_time_string
from astro_pointer.constants import Astrodata


async def astro_data_subscription(context: CallbackContext) -> None:
    await show_astro_data(update=None, context=context)


async def show_astro_data(update: Update, context: CallbackContext) -> None:
    """Send a list of astronomical data to the user."""

    if update is None:
        user_id = context.job.user_id
        chat_id = context.job.chat_id
    else:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data is not None:
        lat = data["latitude"]
        longi = data["longitude"]

        tble = fetch_astro_data(lat, longi)
        current_date_time = get_current_date_time_string(data["utc_offset"])

        await context.bot.send_message(
            chat_id = chat_id,
            text = ("🌠 <b>Astronomical data</b> 🔭\n"
                    f"<code>{tabulate(tble, tablefmt='simple')}</code> \n"

                    f"({current_date_time}) \n"),
            parse_mode = ParseMode.HTML,
            reply_markup = Astrodata.REFRESH_BUTTON
        )

    else:
        await context.bot.send_message(
            chat_id = chat_id,
            text = "I need your location to get the astronomical data. /setlocation to start off."
        )


async def update_astro_data(update: Update, context: CallbackContext) -> str:
    """Update a list of astronomical data by editing the original message.

    Returns:
        str: Output text to be shown to users
    """

    user_id = update.effective_user.id
    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data is not None:
        lat = data["latitude"]
        longi = data["longitude"]

        tble = fetch_astro_data(lat, longi)
        current_date_time = get_current_date_time_string(data["utc_offset"])

        new_text = ("🌠 <b>Astronomical data</b>: \n"
                    f"<code>{tabulate(tble, tablefmt='simple')}</code> \n"
                    f"({current_date_time}) \n")

        await update.callback_query.message.edit_text(
            text = new_text,
            parse_mode = ParseMode.HTML,
            reply_markup = Astrodata.REFRESH_BUTTON
        )

        return "Astrodata refreshed"

    await update.callback_query.message.delete()
    return "I need your location to get the astronomical data."


def fetch_astro_data(latitude, longitude):
    """Fetch a list of astronomical data from weatherapi.com.

    Args:
        latitude (float): latitude of the location
        longitude (float): longitude of the location

    Returns:
        list of list of str : for generating pretty table
    """

    params_inject = {
        "key": Astrodata.API_KEY,
        "q": [latitude, longitude]
    }

    response = requests.get(Astrodata.API_BASE_URL, params=params_inject)
    astro_data = response.json()

    sunrise = astro_data["astronomy"]["astro"]["sunrise"]
    sunset = astro_data["astronomy"]["astro"]["sunset"]
    moonrise = astro_data["astronomy"]["astro"]["moonrise"]
    moonset = astro_data["astronomy"]["astro"]["moonset"]
    moon_phase = astro_data["astronomy"]["astro"]["moon_phase"]
    moon_illumination = astro_data["astronomy"]["astro"]["moon_illumination"]
    # current_date_time = astro_data["location"]["localtime"]

    return [
        ['🌞','Sun'],
        ["Rise", sunrise],
        ["Set", sunset],
        [],
        ['🌝', 'Moon'],
        ["Rise", moonrise],
        ["Set", moonset],
        ["Phase", f"{moon_phase} {Astrodata.MOON_PHASE_DICT[moon_phase]}"],
        ["Illum.", f"{moon_illumination}%"]
    ]
