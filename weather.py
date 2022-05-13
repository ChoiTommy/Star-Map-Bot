import main
import json, urllib.request, ssl
import time
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

def show_weather_data(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)

    if user_id in data:
        lat = data[user_id]["latitude"]
        longi = data[user_id]["longitude"]

        context = ssl._create_unverified_context()
        WEATHER_API_URL = f"https://api.weatherapi.com/v1/current.json?key={main.WEATHER_API_KEY}&q={lat},{longi}"
        with urllib.request.urlopen(WEATHER_API_URL, context=context) as weather_file:
            weather_data = json.load(weather_file)

        current_condition_text = weather_data["current"]["condition"]["text"]
        current_condition_icon_url = weather_data["current"]["condition"]["icon"]
        temperature = weather_data["current"]["temp_c"]
        precipitaion_mm = weather_data["current"]["precip_mm"]
        cloud_percentage = weather_data["current"]["cloud"]

        current_timestamp = int(time.time()) # in UTC
        current_date_time = datetime.utcfromtimestamp(current_timestamp + data[user_id]["utcOffset"]/1000)

        update.message.reply_photo(
            photo = f"https:{current_condition_icon_url}",
            caption = f"""
The weather now is <b>{current_condition_text}</b> at a temperature of <b>{temperature}°C</b>. Precipitation is <b>{precipitaion_mm}mm</b>, with cloud coverage of <b>{cloud_percentage}%</b>.
({current_date_time})

Be prepared before setting out for stargazing!
            """,
            parse_mode = ParseMode.HTML
        )
    else:
        update.message.reply_text("Please set your location with /setlocation first!")