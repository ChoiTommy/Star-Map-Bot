"""
astrodata is a module that consists of functions fetching and displaying astronomical data.

Usage:
Command /astrodata is defined by show_astro_data
"""

import main
import json, urllib.request, ssl
from telegram import Update, ParseMode
from telegram.ext import CallbackContext


moon_phase_dict = { # dict for getting the corresponding moon phase emojis
    "New Moon" : "🌑",
    "Waxing Crescent" : "🌒",
    "First Quarter" : "🌓",
    "Waxing Gibbous" : "🌔",
    "Full Moon" : "🌕",
    "Waning Gibbous" : "🌖",
    "Last Quarter" : "🌗",
    "Waning Crescent" : "🌘"
}


async def show_astro_data(update: Update, context: CallbackContext) -> None:
    """Fetch and send a list of astronomical data to the user."""

    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)

    if user_id in data:
        lat = data[user_id]["latitude"]
        longi = data[user_id]["longitude"]

        context = ssl._create_unverified_context()
        WEATHER_API_URL = f"https://api.weatherapi.com/v1/astronomy.json?key={main.WEATHER_API_KEY}&q={lat},{longi}"
        with urllib.request.urlopen(WEATHER_API_URL, context=context) as astro_file:
            astro_data = json.load(astro_file)

        sunrise = astro_data["astronomy"]["astro"]["sunrise"]
        sunset = astro_data["astronomy"]["astro"]["sunset"]
        moonrise = astro_data["astronomy"]["astro"]["moonrise"]
        moonset = astro_data["astronomy"]["astro"]["moonset"]
        moon_phase = astro_data["astronomy"]["astro"]["moon_phase"]
        moon_illumination = astro_data["astronomy"]["astro"]["moon_illumination"]
        current_date_time = astro_data["location"]["localtime"]

        await update.message.reply_text(
            text = ("🌠<b>Astronomical data</b>: \n"
                    f"Sunrise: {sunrise} \n"
                    f"Sunset: {sunset} \n"
                    f"Moonrise: {moonrise} \n"
                    f"Moonset: {moonset} \n"
                    f"Moon phase: {moon_phase} {moon_phase_dict[moon_phase]} \n"
                    f"Moon illumination: {moon_illumination} \n\n"

                    f"({current_date_time}) \n"
            ),
            parse_mode = ParseMode.HTML
        )

    else:
        await update.message.reply_text("Please set your location with /setlocation first!")