"""
settings is a module that consists of functions setting up and updating user's location.

Usage:
Command /setlocation is defined by set_location and update_location
Command /cancel is defined by cancel. It functions the same as userinfo.cancel_deletion
"""

import helpers
import requests
from firebase_admin import db
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler


def set_location(update: Update, context: CallbackContext) -> int:
    """If their record exists, ask users if they want to update their location. Return 0 to proceed to update_location."""

    user_id = str(update.effective_user.id)

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:
        update.message.reply_text(f"Your current location is {data['latitude']}, {data['longitude']} ({data['address']}).")
        update.message.reply_text("Send your new location if you wish to change. /cancel to keep the current setting.")
    else:
        update.message.reply_text(
            text = "Send your location to me :O Trust me I won\'t tell others\. ||~\(unless someone pays me A LOT\)~|| ",
            parse_mode = ParseMode.MARKDOWN_V2
        )
    return 0 # proceed to update_location


def update_location(update: Update, context: CallbackContext) -> int:
    """Read in a location from the user. Fetch the address string from nominatim reverse API. Save/Update the record. Return ConversationHandler.END."""

    user_id = str(update.effective_user.id)
    lat = update.message.location.latitude
    longi = update.message.location.longitude

    NOMINATIM_REVERSE_API = ("https://nominatim.openstreetmap.org/reverse"
                            "?format=jsonv2"
                            f"&lat={lat}"
                            f"&lon={longi}"
                            "&accept-language=en-US"
                            "&zoom=14")

    response = requests.get(NOMINATIM_REVERSE_API)
    address_data = response.json()

    if "error" in address_data: # Safeguarding, "Unable to geocode"
        update.message.reply_text("You are in the middle of nowhere, my man. Send me a new location of a less remote place, please.")
        return 0 # ask for a new location until user has given a valid one

    else:
        address_string = address_data["display_name"] # from nominatim
        utcOffset = int(helpers.get_offset(lat, longi) * 1000) # in ms

        ref = db.reference(f"/Users/{user_id}")
        data = ref.get()

        if data == None:
            ref.set({"username": update.effective_user.username, "latitude": lat, "longitude" : longi, "address" : address_string, "utcOffset" : utcOffset})
        else:
            ref.update({
                "latitude" : lat,
                "longitude" : longi,
                "address" : address_string,
                "utcOffset" : utcOffset
            })

        update.message.reply_text(f"All set! Your new location is {lat}, {longi} ({address_string}).")
        return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Exit from the ConversationHandler. Halt the location setting process. Return ConversationHandler.END."""

    update.message.reply_text('ℹ️The setup process has been cancelled.')
    return ConversationHandler.END