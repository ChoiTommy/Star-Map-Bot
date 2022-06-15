"""
A module handles callback queries

"""

from starmapbot.features import (
    weather,
    astrodata,
    starmap,
    sun
)
from starmapbot.constants import Weather, Astrodata, Starmap, Sun
from telegram import Update
from telegram.ext import CallbackContext


async def callback(update: Update, context: CallbackContext) -> None:
    """Method for handling callback queries."""

    query = update.callback_query

    if query.data == Weather.REFRESH_CALLBACK_DATA:
        status = await weather.update_weather_data(update, context)
        await query.answer(text=status)

    elif query.data == Astrodata.REFRESH_CALLBACK_DATA:
        status = await astrodata.update_astro_data(update, context)
        await query.answer(text=status)

    elif query.data == Starmap.REFRESH_CALLBACK_DATA:
        status = await starmap.update_star_map(update, context)
        await query.answer(text=status)

    elif Sun.UPDATE_PHOTO in query.data:
        status = await sun.update_sun_photo(update, context)
        await query.answer(text=status)

    elif Sun.SHOW_DESCRIPTION in query.data:
        status = await sun.show_description(update, context)
        await query.answer(text=status)

    elif Sun.HIDE_DESCRIPTION in query.data:
        status = await sun.hide_description(update, context)
        await query.answer(text=status)

    else:
        await query.answer()
