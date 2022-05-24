"""
astrodata is a module that consists of functions fetching and displaying astronomical data.

Usage:
Command /astrodata is defined by show_astro_data
"""

import constants
import requests
from firebase_admin import db
from telegram import Update, ParseMode
from telegram.ext import CallbackContext


def show_astro_data(update: Update, context: CallbackContext) -> None:
    """Fetch and send a list of astronomical data to the user."""

    user_id = str(update.effective_user.id)
    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:
        lat = data["latitude"]
        longi = data["longitude"]

        WEATHER_API_URL = ("https://api.weatherapi.com/v1/"
                            "astronomy.json"
                            f"?key={constants.WEATHER_API_KEY}"
                            f"&q={lat},{longi}")

        response = requests.get(WEATHER_API_URL)
        astro_data = response.json()

        sunrise = astro_data["astronomy"]["astro"]["sunrise"]
        sunset = astro_data["astronomy"]["astro"]["sunset"]
        moonrise = astro_data["astronomy"]["astro"]["moonrise"]
        moonset = astro_data["astronomy"]["astro"]["moonset"]
        moon_phase = astro_data["astronomy"]["astro"]["moon_phase"]
        moon_illumination = astro_data["astronomy"]["astro"]["moon_illumination"]
        current_date_time = astro_data["location"]["localtime"]

        update.message.reply_text(
            text = ("🌠<b>Astronomical data</b>: \n"
                    f"Sunrise: {sunrise} \n"
                    f"Sunset: {sunset} \n"
                    f"Moonrise: {moonrise} \n"
                    f"Moonset: {moonset} \n"
                    f"Moon phase: {moon_phase} {constants.MOON_PHASE_DICT[moon_phase]} \n"
                    f"Moon illumination: {moon_illumination}% \n\n"

                    f"({current_date_time}) \n"),
            parse_mode = ParseMode.HTML
        )

    else:
        update.message.reply_text("Please set your location with /setlocation first!")