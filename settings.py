"""
settings is a module that consists of functions setting up and updating user's location. Some helper functions are also involved.

Usage:
Command /setlocation is defined by set_location and update_location
Command /cancel is defined by cancel. It functions the same as userinfo.cancel_deletion
"""

import json
# import logging
import urllib.request, ssl
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from datetime import datetime
from pytz import timezone, utc
from timezonefinder import TimezoneFinder


tf = TimezoneFinder()


def get_offset(lat, longi):
    """Returns a location's timezone offset from UTC in seconds.

    Args:
        lat (float): Latitude of a point.
        longi (float): Longitude of a point.

    Returns:
        float: Timezone offset from UTC in seconds.
    """

    today = datetime.now()
    tz_target = timezone(tf.certain_timezone_at(lng=longi, lat=lat))
    # ATTENTION: tz_target could be None! handle error case
    today_target = tz_target.localize(today)
    today_utc = utc.localize(today)
    return (today_utc - today_target).total_seconds()


def set_location(update: Update, context: CallbackContext) -> int:
    """If their record exists, ask users if they want to update their location. Return 0 to proceed to update_location."""

    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)
    context.user_data["JSON"] = data

    if user_id in data:
        update.message.reply_text(f"Your current location is {data[user_id]['latitude']}, {data[user_id]['longitude']} ({data[user_id]['address']}).")
        update.message.reply_text("Send your new location if you wish to change. /cancel to keep the current setting.")
    else:
        update.message.reply_text(
            text = "Send your location to me :O Trust me I won\'t tell others ~\(unless someone pays me A LOT\)~ ",
            parse_mode = ParseMode.MARKDOWN_V2
        )
    return 0 # proceed to update_location


def update_location(update: Update, context: CallbackContext) -> int:
    """Read in a location from the user. Fetch the address string from nominatim reverse API. Save/Update the record. Return ConversationHandler.END."""

    user_id = str(update.effective_user.id)
    lat = update.message.location.latitude
    longi = update.message.location.longitude
    data = context.user_data["JSON"]

    context = ssl._create_unverified_context()
    NOMINATIM_REVERSE_API = ("https://nominatim.openstreetmap.org/reverse"
                            "?format=jsonv2"
                            f"&lat={lat}"
                            f"&lon={longi}"
                            "&accept-language=en-US"
                            "&zoom=14")

    # logging.info(NOMINATIM_REVERSE_API)
    with urllib.request.urlopen(NOMINATIM_REVERSE_API, context=context) as address_file:
        address_data = json.load(address_file)

    if "error" in address_data: # Safeguarding, "Unable to geocode"
        update.message.reply_text("You are in the middle of nowhere, my man. Send me a new location of a less remote place, please.")
        return 0 # ask for a new location until user has given a valid one

    else:
        address_string = address_data["display_name"]

        utcOffset = int(get_offset(lat, longi) * 1000) # in ms

        if user_id not in data:
            data.update({user_id:{"username": update.effective_user.username, "latitude": lat, "longitude" : longi, "address" : address_string, "utcOffset" : utcOffset}})
        else:
            data[user_id]["latitude"] = lat
            data[user_id]["longitude"] = longi
            data[user_id]["address"] = address_string
            data[user_id]["utcOffset"] = utcOffset

        with open("locations.json", 'w') as file:
            json.dump(data, file, indent = 4)
        update.message.reply_text(f"All set! Your new location is {lat}, {longi} ({address_string}).")
        return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Exit from the ConversationHandler. Halt the location setting process. Return ConversationHandler.END."""

    update.message.reply_text('ℹ️The setup process has been cancelled.')
    return ConversationHandler.END