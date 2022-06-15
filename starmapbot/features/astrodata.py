"""
A module consists of functions fetching and displaying astronomical data

Usage:
Command /astrodata is defined by show_astro_data
"""

from starmapbot.helpers import get_current_date_time_string
from starmapbot.constants import Astrodata
import requests
from firebase_admin import db
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, error
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from tabulate import tabulate


async def show_astro_data(update: Update, context: CallbackContext) -> None:
    """Send a list of astronomical data to the user."""

    user_id = str(update.effective_user.id)
    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:
        lat = data["latitude"]
        longi = data["longitude"]

        tble = fetch_astro_data(lat, longi)
        current_date_time = get_current_date_time_string(data["utcOffset"]/1000)

        await update.message.reply_html(
            text = ("🌠 <b>Astronomical data</b>: \n"
                    f"<code>{tabulate(tble, tablefmt='simple')}</code> \n"

                    f"({current_date_time}) \n"),
            reply_markup = Astrodata.REFRESH_BUTTON
        )

    else:
        await update.message.reply_text("Please set your location with /setlocation first!")


async def update_astro_data(update: Update, context: CallbackContext) -> str:
    """Update a list of astronomical data by editing the original message.

    Returns:
        str: Output text to be shown to users
    """

    user_id = str(update.effective_user.id)
    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:
        lat = data["latitude"]
        longi = data["longitude"]

        tble = fetch_astro_data(lat, longi)
        current_date_time = get_current_date_time_string(data["utcOffset"]/1000)

        new_text = ("🌠 <b>Astronomical data</b>: \n"
                    f"<code>{tabulate(tble, tablefmt='simple')}</code> \n"
                    f"({current_date_time}) \n")

        await update.callback_query.message.edit_text(
            text = new_text,
            parse_mode = ParseMode.HTML,
            reply_markup = Astrodata.REFRESH_BUTTON
        )

        return "Astrodata refreshed"

    else:
        await update.callback_query.message.delete()
        return "Please set your location first!"


def fetch_astro_data(latitude, longitude):
    """Fetch a list of astronomical data from weatherapi.com.

    Args:
        latitude (float): latitude of the location
        longitude (float): longitude of the location

    Returns:
        list of list of str : for generating pretty table
        ~~str : Current date and time~~
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
