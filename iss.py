"""

"""

import requests, time
from telegram import Update, Location
from telegram.ext import ContextTypes


ISS_LOCATION_URL = "http://api.open-notify.org/iss-now.json"


async def iss_live_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # todo concurrency
    for i in range(10):

        response = requests.get(ISS_LOCATION_URL)
        iss_location_data = response.json()

        lat = iss_location_data["iss_position"]["latitude"]
        lon = iss_location_data["iss_position"]["longitude"]

        loc = Location(longitude=lon, latitude=lat)

        if i == 0:
            msg = await update.message.reply_location(
                location = loc,
                live_period = 120        # in seconds
            )
        else:
            await msg.edit_live_location(
                location = loc
            )

        time.sleep(10)