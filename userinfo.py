"""
userinfo is a module that consists of functions regarding displaying, setting up, and deleting user's info.

Usage:
Command /myinfo is defined by show_user_info
Command /deletemyinfo is defined by deletion_confirmation and delete_user_info
Command /cancel is defined by cancel_location_setup or cancel_deletion
"""

import helpers
import requests
from firebase_admin import db
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler


def show_user_info(update: Update, context: CallbackContext) -> None:
    """Display user info when the command /myinfo is called. User info consists of latitude, longitude, address and timezone."""

    user_id = str(update.effective_user.id)
    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:
        msg = update.message.reply_location(latitude=data["latitude"], longitude=data["longitude"])
        update.message.reply_html(
            text = (f'Hi {update.effective_user.mention_html()}, \n'
                    'Your currently set location is \n'
                    f'Latitude: {data["latitude"]} \n'
                    f'Longitude: {data["longitude"]} \n'
                    f'Location: <i>{data["address"]}</i> \n'
                    f'Timezone: {helpers.utcOffset_to_tzstring(data["utcOffset"])} \n\n'

                    '/setlocation to modify. /deletemyinfo to delete your data. \n'),
            reply_to_message_id = msg.message_id
        )
    else:
        update.message.reply_html(
            text = (f'Hi {update.effective_user.mention_html()}, \n'
                    'You have yet to set any location. \n'
                    '/setlocation to start off. \n')
        )


def set_location(update: Update, context: CallbackContext) -> int:
    """If their record exists, ask users if they want to update their location. Return 0 to proceed to update_location."""

    user_id = str(update.effective_user.id)

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data != None:
        update.message.reply_text(f"Your location is {data['latitude']}, {data['longitude']} ({data['address']}).")
        update.message.reply_markdown_v2("Send your new location \(Telegram location or a stirng in `lat, lon` format\) if you wish to change\. \n/cancel to keep the current setting\.")
    else:
        update.message.reply_markdown_v2(
            text = ("Send your location to me \(Either a Telegram location object or a string in the format of `lat: float, lon: float`\) \n"
                    "Trust me I won\'t tell others :O ||~\(unless someone pays me A LOT\)~|| "),
        )
    return 0 # proceed to update_location


def update_location(update: Update, context: CallbackContext) -> int:
    """Read in a location from the user. Fetch the address string from nominatim reverse API. Save/Update the record. Return ConversationHandler.END."""

    user_id = str(update.effective_user.id)

    if update.message.location != None:
        lat, longi = update.message.location.latitude, update.message.location.longitude
    else:
        lat = float(update.message.text[:update.message.text.find(',')])
        longi = float(update.message.text[update.message.text.find(',')+1:])

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
            username = update.effective_user.username
            ref.set({
                "username": username if username is not None else "None",
                "latitude": lat,
                "longitude": longi,
                "address": address_string,
                "utcOffset": utcOffset,
                "creation_timestamp": helpers.get_current_date_time_string()  # UTC time
            })
        else:
            ref.update({
                "latitude" : lat,
                "longitude" : longi,
                "address" : address_string,
                "utcOffset" : utcOffset,
                "update_timestamp": helpers.get_current_date_time_string()  # UTC time
            })

        update.message.reply_text(f"All set! Your new location is {lat}, {longi} ({address_string}).")
        return ConversationHandler.END


def cancel_location_setup(update: Update, context: CallbackContext) -> int:
    """Exit from the ConversationHandler. Halt the location setting process. Return ConversationHandler.END."""

    update.message.reply_text('ℹ️The setup process has been cancelled.')
    return ConversationHandler.END


def deletion_confirmation(update: Update, context: CallbackContext) -> int:
    """Ask for confirmation to delete the user info from the server. Return Conversation.END if user has no data on the server, else returns 0."""

    user_id = str(update.effective_user.id)
    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data == None:
        update.message.reply_text(
            text = ("Hi new user, rest assured we have not collected any data from you, so nothing has been erased. "
                    "Perhaps you can try /setlocation and give me something to delete afterwards?")
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            "Are you sure you want to delete your location data? Note that this action cannot be undone.",
            reply_markup = ReplyKeyboardMarkup([['Yes', 'No']], resize_keyboard = True)
        )
        return 0


def delete_user_info(update: Update, context: CallbackContext) -> int:
    """Perform deletion on users' data if 'Yes' is retrieved. Return ConversationHandler.END to halt the ConversationHandler."""

    if update.message.text == "Yes":
        user_id = str(update.effective_user.id)
        ref = db.reference(f"/Users/{user_id}")
        ref.set({})     # delete the record

        update.message.reply_text(
            text = ("Voilà! I have erased your existence. Keep it up and leave no trace in the cyber world! \n"
                    "/myinfo <- click it to see for yourself, scumbag"),
            reply_markup = ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        return cancel_deletion(update, context)


def cancel_deletion(update: Update, context: CallbackContext) -> int:
    """Cancel the deletion operation with the command /cancel. Return ConversationHandler.END"""

    update.message.reply_text("Got it! My generous user. Your data are still in my hands.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END