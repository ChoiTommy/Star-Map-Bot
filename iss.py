"""
iss is a module that consists of functions fetching and displaying live location of the International Space Station.

Usage:
Command /iss is defined by iss_live_location
"""

import requests, asyncio
from telegram import Update, Location
from telegram.ext import CallbackContext


ISS_LOCATION_URL = "http://api.open-notify.org/iss-now.json"


async def iss_live_location(update: Update, context: CallbackContext) -> None:

    title = await update.message.reply_text("🛰 ISS Live Location:")

    for i in range(20):

        response = requests.get(ISS_LOCATION_URL)
        iss_location_data = response.json()

        lat = iss_location_data["iss_position"]["latitude"]
        lon = iss_location_data["iss_position"]["longitude"]

        loc = Location(longitude=lon, latitude=lat)

        if i == 0:
            msg = await update.message.reply_location(
                location = loc,
                live_period = 120,        # in seconds
                reply_to_message_id = title.message_id
            )
        else:
            await msg.edit_live_location(
                location = loc
            )

        await asyncio.sleep(5)   # location data updates every 5 secs

    await title.edit_text(text="🛰 ISS Live Location session has ended.")