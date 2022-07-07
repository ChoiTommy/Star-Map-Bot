"""
A module consists of functions fetching and displaying live location of the International Space Station

Usage:
Command /iss is defined by iss_live_location
"""

import asyncio
import requests
from telegram import Update, Location
from telegram.ext import CallbackContext
from astro_pointer.constants import ISS


async def iss_subscription(context: CallbackContext) -> None:
    await iss_live_location(update=None, context=context)


async def iss_live_location(update: Update, context: CallbackContext) -> None:
    """Send a live location of the International Space Station to the user."""

    chat_id = context.job.chat_id if update is None else update.effective_chat.id

    title = await context.bot.send_message(chat_id=chat_id, text="🛰 ISS Live Location:")

    for i in range(20):

        response = requests.get(ISS.API_BASE_URL)
        iss_location_data = response.json()

        lat = iss_location_data["iss_position"]["latitude"]
        lon = iss_location_data["iss_position"]["longitude"]

        loc = Location(longitude=lon, latitude=lat)

        if i == 0:
            msg = await context.bot.send_location(
                chat_id = chat_id,
                location = loc,
                live_period = 130,        # in seconds
                reply_to_message_id = title.message_id
            )
        else:
            await msg.edit_live_location(
                location = loc
            )

        await asyncio.sleep(5)   # location data updates every 5 secs

    await title.edit_text(text="🛰 ISS Live Location session has ended.")
