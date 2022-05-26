"""
starmap is a module that consists of functions fetching and forwarding a star map (sky chart) to user.

Usage:
Command /starmap is defined by send_star_map
"""

import constants, helpers
import time
import requests
from firebase_admin import db
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaDocument
from telegram.ext import CallbackContext
import fitz


REFRESH_STARMAP_BUTTON = InlineKeyboardMarkup([
                            [InlineKeyboardButton("Refresh", callback_data=constants.REFRESH_STARMAP_CALLBACK_DATA)]
                        ])
# Star map URL
STAR_MAP_URL = "https://www.heavens-above.com/SkyAndTelescope/StSkyChartPDF.ashx"
# params to be injected: time, latitude, longitude, location, utcOffset(in ms)
REST_OF_THE_URL = ("&showEquator=false"         # TODO switch to a dict header
                    "&showEcliptic=true"
                    "&showStarNames=true"
                    "&showPlanetNames=true"
                    "&showConsNames=true"
                    "&showConsLines=true"
                    "&showConsBoundaries=false"
                    "&showSpecials=false"
                    "&use24hClock=true")


def send_star_map(update: Update, context: CallbackContext) -> None:
    """Forward a star map to user based on the set location and the current time."""

    user_id = str(update.effective_user.id)

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:

        lat = str(data["latitude"])
        longi = str(data["longitude"])
        address = data["address"].replace(',', "%2c").replace(' ', "%20")
        utcOffset = str(data["utcOffset"])

        current_date_time = helpers.get_current_date_time_string(data["utcOffset"]/1000)

        pix = fetch_star_map(lat, longi, address, utcOffset)

        # update.message.reply_document(document = fetch_target) # pdf
        update.message.reply_document(
            document = pix.tobytes(),
            filename = f"Star_Map_{current_date_time.replace(' ', '_').replace(':', '_')}.png",
            caption = f"Enjoy the stunning stars! Be considerate and leave no trace while stargazing! \n ({current_date_time})",
            reply_markup = REFRESH_STARMAP_BUTTON
        )

    else:
        update.message.reply_text("Please set your location with /setlocation first!")


def update_star_map(update: Update, context: CallbackContext) -> str:
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
        address = data["address"].replace(',', "%2c").replace(' ', "%20")
        utcOffset = str(data["utcOffset"])

        current_date_time = helpers.get_current_date_time_string(data["utcOffset"]/1000)

        pix = fetch_star_map(lat, longi, address, utcOffset)

        update.callback_query.message.edit_media(
            media = InputMediaDocument(media=pix.tobytes(), filename=f"Star_Map_{current_date_time.replace(' ', '_').replace(':', '_')}.png"),
        ).edit_caption(
            caption = f"Enjoy the stunning stars! Be considerate and leave no trace while stargazing! \n ({current_date_time})",
            reply_markup = REFRESH_STARMAP_BUTTON
        )

        return "Star map updated"
    else:
        update.callback_query.message.edit_caption().delete()
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

    fetch_target = (f"{STAR_MAP_URL}"
                    f"?time={str(int(time.time()*1000))}" # time.time(): seconds (floating point) since the epoch in UTC
                    f"&latitude={latitude}"
                    f"&longitude={longitude}"
                    f"&location={address}"
                    f"&utcOffset={utcOffset}"
                    f"{REST_OF_THE_URL}")

    response = requests.get(fetch_target) # Download the data behind the URL
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