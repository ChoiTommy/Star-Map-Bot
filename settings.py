import json
import urllib.request, ssl
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from datetime import datetime
from pytz import timezone, utc
from timezonefinder import TimezoneFinder

tf = TimezoneFinder()

def get_offset(lat, longi):
    """
    returns a location's time zone offset from UTC in seconds.
    """
    today = datetime.now()
    tz_target = timezone(tf.certain_timezone_at(lng=longi, lat=lat))
    # ATTENTION: tz_target could be None! handle error case
    today_target = tz_target.localize(today)
    today_utc = utc.localize(today)
    return (today_utc - today_target).total_seconds()

def set_location(update: Update, context: CallbackContext) -> int:
    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)
    context.user_data["JSON"] = data

    if data.get(user_id) != None:
        update.message.reply_text(f"Your current location is {data[user_id]['latitude']}, {data[user_id]['longitude']} ({data[user_id]['address']}).")
        update.message.reply_text("Send your new location if you wish to change. /cancel to keep the current setting.")
    else:
        update.message.reply_text("Send your location to me :O Trust me I won\'t tell others ~\(unless someone pays me A LOT\)~ ", parse_mode = ParseMode.MARKDOWN_V2)
    return 0

def update_location(update: Update, context: CallbackContext) -> int:
    user_id = str(update.effective_user.id)
    lat = update.message.location.latitude
    longi = update.message.location.longitude
    data = context.user_data["JSON"]

    context = ssl._create_unverified_context()
    NOMINATIM_REVERSE_API = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={longi}&accept-language=en-US"
    # print(NOMINATIM_REVERSE_API)
    with urllib.request.urlopen(NOMINATIM_REVERSE_API, context=context) as address_file:
        address_data = json.load(address_file)

    # address_string = f"{address_data['address']['suburb']}, {address_data['address']['country']}"
    address_string = address_data["display_name"] #todo extract general location only

    utcOffset = int(get_offset(lat, longi) * 1000) # in ms

    if data.get(user_id) == None:
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
    update.message.reply_text('ℹ️The setup process is cancelled.')
    return ConversationHandler.END