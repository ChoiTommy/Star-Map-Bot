"""
callback_queries is a module for handling callback queries.

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

    elif "SUN" in query.data:
        status = await sun.update_sun_photo(update, context)
        await query.answer(text=status)

    elif "SHOW" in query.data:
        status = await sun.show_description(update, context)
        await query.answer(text=status)

    elif "HIDE" in query.data:
        status = await sun.hide_description(update, context)
        await query.answer(text=status)

    else:
        await query.answer()
