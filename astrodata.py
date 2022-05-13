import main
import json, urllib.request, ssl
import time
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# WEATHER_API_URL = f"https://api.weatherapi.com/v1/astronomy.json?key={main.WEATHER_API_KEY}"# &q=1.354069,103.687933&dt=2022-05-08

moon_phase_dict = {
    "New Moon" : "🌑",
    "Waxing Crescent" : "🌒",
    "First Quarter" : "🌓",
    "Waxing Gibbous" : "🌔",
    "Full Moon" : "🌕",
    "Waning Gibbous" : "🌖",
    "Last Quarter" : "🌗",
    "Waning Crescent" : "🌘"
}

def show_astro_data(update: Update, context: CallbackContext) -> None:
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

        current_timestamp = int(time.time()) # in UTC
        current_date_time = datetime.utcfromtimestamp(current_timestamp + data[user_id]["utcOffset"]/1000)

        update.message.reply_text(
            f"""
🌠<b>Astronomical data</b>:
Sunrise: {sunrise}
Sunset: {sunset}
Moonrise: {moonrise}
Moonset: {moonset}
Moon phase: {moon_phase} {moon_phase_dict[moon_phase]}
Moon illumination: {moon_illumination}

({current_date_time})
            """,
            parse_mode=ParseMode.HTML
        )
    else:
        update.message.reply_text("Please set your location with /setlocation first!")