"""
A module consists of functions fetching and displaying weather data relevant to stargazing

Usage:
Command /weather is defined by show_weather_data
"""

import requests
from firebase_admin import db
from telegram import Update, InputMediaPhoto
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from tabulate import tabulate
from astro_pointer.helpers import get_current_date_time_string
from astro_pointer.constants import Weather


async def weather_subscription(context: CallbackContext) -> None:
    await show_weather_data(update=None, context=context)


async def show_weather_data(update: Update, context: CallbackContext) -> None:
    """Send a simple weather report showing weather data necessary for stargazing."""

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

        tble, current_condition_icon_url, current_condition_text = fetch_weather_data(lat, longi)
        current_date_time = get_current_date_time_string(data["utc_offset"])

        await context.bot.send_photo(
            chat_id = chat_id,
            photo = f"https:{current_condition_icon_url}",
            caption = (f"Weather now is: <b>{current_condition_text}</b> \n"

                        f"<code>{tabulate(tble, tablefmt='fancy_grid')}</code> \n"
                        f"({current_date_time}) \n\n"

                        "Be prepared before setting out for stargazing!"),
            parse_mode = ParseMode.HTML,
            reply_markup = Weather.REFRESH_BUTTON
        )

    else:
        await context.bot.send_message(
            chat_id = chat_id,
            text = "Tell me a location with /setlocation first to use this feature."
        )


async def update_weather_data(update: Update, context: CallbackContext) -> str:
    """Update weather data by editing the original message.

        Returns:
        str: Output text to be shown to users
    """

    user_id = update.effective_user.id
    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data is not None:
        lat = data["latitude"]
        longi = data["longitude"]

        tble, current_condition_icon_url, current_condition_text = fetch_weather_data(lat, longi)
        current_date_time = get_current_date_time_string(data["utc_offset"])

        await update.callback_query.message.edit_media(
            media = InputMediaPhoto(
                media = f"https:{current_condition_icon_url}",
                caption = (f"Weather now is: <b>{current_condition_text}</b> \n"

                            f"<code>{tabulate(tble, tablefmt='fancy_grid')}</code> \n"
                            f"({current_date_time}) \n\n"

                            "Be prepared before setting out for stargazing!"),
                parse_mode = ParseMode.HTML
            ),
            reply_markup = Weather.REFRESH_BUTTON
        )

        return "Weather refreshed"
    else:
        await update.callback_query.message.delete()
        return "Set a location first to use this feature."


def fetch_weather_data(latitude, longitude):
    """Fetch weather data from weatherapi.com.

    Args:
        latitude (float): latitude of the location
        longitude (float): longitude of the location

    Returns:
        list of list of str: for generating pretty table
        str : URL to the icon of current condition
        str : Description of the current condition
    """

    params_inject = {
        "key": Weather.API_KEY,
        "q": [latitude, longitude]
    }

    response = requests.get(Weather.API_BASE_URL, params=params_inject)
    weather_data = response.json()

    current_condition_text = weather_data["current"]["condition"]["text"]
    current_condition_icon_url = weather_data["current"]["condition"]["icon"]
    temperature = weather_data["current"]["temp_c"]
    precipitation_mm = weather_data["current"]["precip_mm"]
    cloud_percentage = weather_data["current"]["cloud"]
    visibility_km = weather_data["current"]["vis_km"]
    humidity = weather_data["current"]["humidity"]
    uv_index = weather_data["current"]["uv"]

    # current_date_time = weather_data["location"]["localtime"]

    return [
        ["Temp.", f"{temperature}°C"],
        ["Precip.", f"{precipitation_mm} mm"],
        ["Cloud", f"{cloud_percentage}%"],
        ["Visibility", f"{visibility_km} km"],
        ["Humidity", f"{humidity}%"],
        ["UV index", uv_index]
    ], current_condition_icon_url, current_condition_text
