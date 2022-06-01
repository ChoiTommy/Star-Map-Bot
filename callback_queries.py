"""
callback_queries is a module for handling callback queries.

"""
import weather, astrodata, starmap, sun, constants

from telegram import Update
from telegram.ext import CallbackContext


def callback(update: Update, context: CallbackContext) -> None:
    """Method for handling callback queries."""

    query = update.callback_query

    if query.data == constants.REFRESH_WEATHER_CALLBACK_DATA:
        status = weather.update_weather_data(update, context)
        query.answer(text=status)

    elif query.data == constants.REFRESH_ASTRODATA_CALLBACK_DATA:
        status = astrodata.update_astro_data(update, context)
        query.answer(text=status)

    elif query.data == constants.REFRESH_STARMAP_CALLBACK_DATA:
        status = starmap.update_star_map(update, context)
        query.answer(text=status)

    elif "SUN" in query.data:
        status = sun.update_sun_pic(update, context)
        query.answer(text=status)

    else:
        query.answer()
