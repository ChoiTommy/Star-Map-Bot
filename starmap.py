"""
starmap is a module that consists of functions fetching and forwarding a star map (sky chart) to user.

Usage:
Command /starmap is defined by send_star_map
"""

import constants, helpers
import time
import requests
from firebase_admin import db
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaDocument
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
import fitz


STAR_MAP_BASE_URL = "https://www.heavens-above.com/SkyAndTelescope/StSkyChartPDF.ashx"
# params to be injected: time, latitude, longitude, location, utcOffset(in ms)
REST_OF_THE_PARAM = {
    "showEquator": False,
    "showEcliptic": True,
    "showStarNames": False,
    "showPlanetNames": True,
    "showConsNames": True,
    "showConsLines": True,
    "showConsBoundaries": False,
    "showSpecials": False,
    "use24hClock": True
}

REFRESH_STARMAP_BUTTON = InlineKeyboardMarkup([
                            [InlineKeyboardButton("Refresh", callback_data=constants.REFRESH_STARMAP_CALLBACK_DATA)]
                        ])


async def send_star_map(update: Update, context: CallbackContext) -> None:
    """Forward a star map to user based on the set location and the current time."""

    user_id = str(update.effective_user.id)

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:

        lat = str(data["latitude"])
        longi = str(data["longitude"])
        address = data["address"]
        utcOffset = str(data["utcOffset"])

        current_date_time = helpers.get_current_date_time_string(data["utcOffset"]/1000)

        pix = fetch_star_map(lat, longi, address, utcOffset)

        # update.message.reply_document(document = fetch_target) # pdf
        await update.message.reply_document(
            document = pix.tobytes(),
            filename = f"Star_Map_{current_date_time.replace(' ', '_').replace(':', '_')}.png",
            caption = f"Enjoy the stunning stars! Be considerate and leave no trace while stargazing! \n ({current_date_time})",
            reply_markup = REFRESH_STARMAP_BUTTON
        )

    else:
        await update.message.reply_text("Please set your location with /setlocation first!")


async def update_star_map(update: Update, context: CallbackContext) -> str:
    """Update the star map by replacing the png with a new one.

    Returns:
        str: Output text to be shown to users
    """

    user_id = str(update.effective_user.id)

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:

        lat = str(data["latitude"])
        longi = str(data["longitude"])
        address = data["address"]
        utcOffset = str(data["utcOffset"])

        current_date_time = helpers.get_current_date_time_string(data["utcOffset"]/1000)

        pix = fetch_star_map(lat, longi, address, utcOffset)

        await update.callback_query.message.edit_media(
            media = InputMediaDocument(
                media = pix.tobytes(),
                filename = f"Star_Map_{current_date_time.replace(' ', '_').replace(':', '_')}.png",
                caption = f"Enjoy the stunning stars! Be considerate and leave no trace while stargazing! \n ({current_date_time})"
            ),
            reply_markup = REFRESH_STARMAP_BUTTON
        )

        return "Star map updated"
    else:
        await update.callback_query.message.delete()
        return "Please set your location first!"


def fetch_star_map(latitude, longitude, address, utcOffset):
    """Fetch a star map from skyandtelescope.com.

    Args:
        latitude (str): latitude of the location
        longitude (str): longitude of the location
        address (str): address text of the above location
        utcOffset (str): UTC offset in ms

    Returns:
        fitz.Pixmap: plane rectangular sets of pixels
    """

    params_inject = {
        "time": int(time.time()*1000), # time.time(): seconds (floating point) since the epoch in UTC
        "latitude": latitude,
        "longitude": longitude,
        "location": address,
        "utcOffset": utcOffset
    }

    response = requests.get(STAR_MAP_BASE_URL, params=params_inject|REST_OF_THE_PARAM) # | to merge two dictionaries
    doc = fitz.open(stream=response.content)
    page = doc.load_page(0)  # number of page
    pix = page.get_pixmap(
        dpi = 200,
        colorspace = fitz.csRGB,
        annots = False,
        clip = fitz.IRect(1, 1, 600, 650)
    )
    pix.tint_with(black=-129010, white=0) # no idea on how these values work, just do trial and error
    doc.close()

    return pix
