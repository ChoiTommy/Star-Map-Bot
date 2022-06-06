"""
weather is a module that consists of functions fetching and displaying weather data relevant to stargazing.

Usage:
Command /weather is defined by show_weather_data
"""

import constants
import requests
from firebase_admin import db
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CallbackContext
from tabulate import tabulate


WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1/current.json"

REFRESH_WEATHER_BUTTON = InlineKeyboardMarkup([
                            [InlineKeyboardButton("Refresh", callback_data=constants.REFRESH_WEATHER_CALLBACK_DATA)]
                        ])


def show_weather_data(update: Update, context: CallbackContext) -> None:
    """Send a simple weather report showing weather data necessary for stargazing."""

    user_id = str(update.effective_user.id)
    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:
        lat = data["latitude"]
        longi = data["longitude"]

        tble, current_condition_icon_url, current_condition_text, current_date_time = fetch_weather_data(lat, longi)

        update.message.reply_photo(
            photo = f"https:{current_condition_icon_url}",
            caption = (f"Weather now is: <b>{current_condition_text}</b> \n"

                        f"<code>{tabulate(tble, tablefmt='fancy_grid')}</code> \n"
                        f"({current_date_time}) \n\n"

                        "Be prepared before setting out for stargazing!"),
            parse_mode = ParseMode.HTML,
            reply_markup = REFRESH_WEATHER_BUTTON
        )

    else:
        update.message.reply_text("Please set your location with /setlocation first!")


def update_weather_data(update: Update, context: CallbackContext) -> str:
    """Update weather data by editing the original message.

        Returns:
        str: Output text to be shown to users
    """

    user_id = str(update.effective_user.id)
    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:
        lat = data["latitude"]
        longi = data["longitude"]

        tble, current_condition_icon_url, current_condition_text, current_date_time = fetch_weather_data(lat, longi)

        update.callback_query.message.edit_media(
            media = InputMediaPhoto(media=f"https:{current_condition_icon_url}")
        ).edit_caption(
            caption = (f"Weather now is: <b>{current_condition_text}</b> \n"

                        f"<code>{tabulate(tble, tablefmt='fancy_grid')}</code> \n"
                        f"({current_date_time}) \n\n"

                        "Be prepared before setting out for stargazing!"),
            parse_mode = ParseMode.HTML,
            reply_markup = REFRESH_WEATHER_BUTTON
        )
        return "Weather refreshed"
    else:
        update.callback_query.message.delete()
        return "Please set your location first!"


def fetch_weather_data(latitude, longitude):
    """Fetch weather data from weatherapi.com.

    Args:
        latitude (float): latitude of the location
        longitude (float): longitude of the location

    Returns:
        list of list : for generating pretty table
        str : URL to the icon of current condition
        str : Description of the current condition
        str : Current date and time
    """

    params_inject = {
        "key": constants.WEATHER_API_KEY,
        "q": [latitude, longitude]
    }

    response = requests.get(WEATHER_API_BASE_URL, params=params_inject)
    weather_data = response.json()

    current_condition_text = weather_data["current"]["condition"]["text"]
    current_condition_icon_url = weather_data["current"]["condition"]["icon"]
    temperature = weather_data["current"]["temp_c"]
    precipitation_mm = weather_data["current"]["precip_mm"]
    cloud_percentage = weather_data["current"]["cloud"]
    visibility_km = weather_data["current"]["vis_km"]
    humidity = weather_data["current"]["humidity"]
    uv_index = weather_data["current"]["uv"]

    current_date_time = weather_data["location"]["localtime"]

    return [
        ["Temp.", f"{temperature}°C"],
        ["Precip.", f"{precipitation_mm} mm"],
        ["Cloud", f"{cloud_percentage}%"],
        ["Visibility", f"{visibility_km} km"],
        ["Humidity", f"{humidity}%"],
        ["UV index", uv_index]
    ], current_condition_icon_url, current_condition_text, current_date_time