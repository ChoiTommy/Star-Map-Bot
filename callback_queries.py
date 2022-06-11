"""
A module handles callback queries

"""
import weather, astrodata, starmap, sun, constants

from telegram import Update
from telegram.ext import CallbackContext


async def callback(update: Update, context: CallbackContext) -> None:
    """Method for handling callback queries."""

    query = update.callback_query

    if query.data == constants.REFRESH_WEATHER_CALLBACK_DATA:
        status = await weather.update_weather_data(update, context)
        await query.answer(text=status)

    elif query.data == constants.REFRESH_ASTRODATA_CALLBACK_DATA:
        status = await astrodata.update_astro_data(update, context)
        await query.answer(text=status)

    elif query.data == constants.REFRESH_STARMAP_CALLBACK_DATA:
        status = await starmap.update_star_map(update, context)
        await query.answer(text=status)

    elif constants.UPDATE_SUN_PHOTO in query.data:
        status = await sun.update_sun_photo(update, context)
        await query.answer(text=status)

    elif constants.SHOW_SUN_DESCRIPTION in query.data:
        status = await sun.show_description(update, context)
        await query.answer(text=status)

    elif constants.HIDE_SUN_DESCRIPTION in query.data:
        status = await sun.hide_description(update, context)
        await query.answer(text=status)

    else:
        await query.answer()
