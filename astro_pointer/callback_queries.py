"""
A module handles callback queries

"""

from astro_pointer.features import (
    weather,
    astrodata,
    starmap,
    sun
)
from astro_pointer.constants import Weather, Astrodata, Starmap, Sun
from telegram import Update
from telegram.ext import CallbackContext


async def callback(update: Update, context: CallbackContext) -> None:
    """Method for handling callback queries."""

    query = update.callback_query

    # Weather refresh
    if query.data == Weather.REFRESH_CALLBACK_DATA:
        status = await weather.update_weather_data(update, context)
        await query.answer(text=status)

    # Astrodata refresh
    elif query.data == Astrodata.REFRESH_CALLBACK_DATA:
        status = await astrodata.update_astro_data(update, context)
        await query.answer(text=status)

    # Star map refresh
    elif query.data == Starmap.REFRESH_CALLBACK_DATA:
        status = await starmap.update_star_map(update, context)
        await query.answer(text=status)

    # Sun
    elif Sun.UPDATE_PHOTO in query.data:
        status = await sun.update_sun_photo(update, context)
        await query.answer(text=status)

    elif Sun.SHOW_DESCRIPTION in query.data:
        status = await sun.show_description(update, context)
        await query.answer(text=status)

    elif Sun.HIDE_DESCRIPTION in query.data:
        status = await sun.hide_description(update, context)
        await query.answer(text=status)

    # Star map preference update
    elif Starmap.PREFERENCE_CALLBACK_DATA in query.data:
        status = await starmap.update_preference(update, context)
        await query.answer(text=status)

    # Star map generation
    elif query.data == Starmap.GENERATE_CALLBACK_DATA:
        _ = await starmap.update_star_map(update, context)
        await query.answer(text="Star map generated")

    else:
        await query.answer()
