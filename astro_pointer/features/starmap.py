"""
A module consists of functions fetching and forwarding a star map (sky chart) to user

Usage:
Command /starmap is defined by send_star_map


Database structure:

"Users": {
        "telegram_user_id_0": {
            "latitude": 0,
            "longitude": 0,
            "address": "Your address",
            "username": "telegram_username_0",
            "utcOffset": 0,
            "creation_timestamp": "1970-01-01 00:00:00",
            "update_timestamp": "1970-01-01 00:00:00",
            "starmap_preferences": {
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
    },
},

"""

from astro_pointer.helpers import get_current_date_time_string
from astro_pointer.constants import Starmap
import time
import requests
from firebase_admin import db
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaDocument, error
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
import fitz


def populate_preference_buttons(user_preferences: dict) -> InlineKeyboardMarkup:
    """Populate the preference buttons for the star map."""

    buttons = []

    for i, name_n_callbackdata in enumerate(Starmap.NAME_TO_CALLBACK_DATA.items()):
        name = name_n_callbackdata[0]
        callbackdata = name_n_callbackdata[1]

        db_key = Starmap.CALLBACK_DATA_TO_DB_KEYS[callbackdata]

        if (i+1) % 2 == 1:
            buttons.append([InlineKeyboardButton(
                text = f"{name} {'✔' if user_preferences[db_key] else '❌'}",
                callback_data = callbackdata
            )])
        else:
            buttons[-1].append(InlineKeyboardButton(
                text = f"{name} {'✔' if user_preferences[db_key] else '❌'}",
                callback_data = callbackdata
            ))

    buttons.append([InlineKeyboardButton(
        text = "Reset to default ↺",
        callback_data = Starmap.RESET_TO_DEFAULT_CALLBACK_DATA)
    ])

    buttons.append([InlineKeyboardButton(
        text = "Generate Star Map →",
        callback_data = Starmap.GENERATE_CALLBACK_DATA
    )])

    return InlineKeyboardMarkup(buttons)


async def preference_message(update: Update, context: CallbackContext) -> None:     # todo better name?
    """Send a message with the current preferences of the user."""

    user_id = update.effective_user.id

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data is not None:
        await update.message.reply_photo(
            photo = open("assets/star_map_params.png", "rb"),
            caption = "Set your star map preferences below:",
            reply_markup = populate_preference_buttons(data["starmap_preferences"])
        )

    else:
        await update.message.reply_text("Please set your location with /setlocation first!")


async def update_preference(update: Update, context: CallbackContext) -> str:
    """Update preferences on the Firebase database."""

    db_key = Starmap.CALLBACK_DATA_TO_DB_KEYS[update.callback_query.data]

    user_id = update.effective_user.id
    ref = db.reference(f"/Users/{user_id}/starmap_preferences")
    user_preferences = ref.get()

    user_preferences[db_key] = not user_preferences[db_key]
    # ref.update(user_preferences)
    ref.update({db_key: user_preferences[db_key]})

    await update.callback_query.message.edit_reply_markup(
        reply_markup = populate_preference_buttons(user_preferences)
    )

    return f"{db_key} is now set to {user_preferences[db_key]}"


async def reset_to_default_preferences(update: Update, context: CallbackContext) -> str:
    """Reset the preferences to default."""

    user_id = update.effective_user.id
    ref = db.reference(f"/Users/{user_id}/starmap_preferences")

    ref.update(Starmap.DEFAULT_PREFERENCES)
    try:
        await update.callback_query.message.edit_reply_markup(
            reply_markup = populate_preference_buttons(Starmap.DEFAULT_PREFERENCES)
        )
    except error.BadRequest:
        pass

    return "Preferences reset to default"


async def star_map_subscription(context: CallbackContext) -> None:
    await send_star_map(update=None, context=context)


async def send_star_map(update: Update, context: CallbackContext) -> None:
    """Forward a star map to user based on the set location and the current time."""

    if update is None:
        user_id = context.job.user_id
        chat_id = context.job.chat_id
    else:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data is not None:

        lat = str(data["latitude"])
        longi = str(data["longitude"])
        address = data["address"]
        utcOffset = data["utcOffset"]
        star_map_param = data["starmap_preferences"]

        current_date_time = get_current_date_time_string(utcOffset)

        pix = fetch_star_map(lat, longi, address, utcOffset, star_map_param)

        # update.message.reply_document(document = fetch_target) # pdf
        await context.bot.send_document(
            chat_id = chat_id,
            document = pix.tobytes(),
            filename = f"Star_Map_{current_date_time.replace(' ', '_').replace(':', '_')}.png",
            caption = f"Enjoy the stunning stars! Be considerate and leave no trace while stargazing! \n ({current_date_time})",
            reply_markup = Starmap.REFRESH_BUTTON
        )

    else:
        await context.bot.send_message(
            chat_id = chat_id,
            text = "Please set your location with /setlocation first!"      # todo better user instructions
        )


async def update_star_map(update: Update, context: CallbackContext) -> str:
    """Update the star map by replacing the png with a new one.

    Returns:
        str: Output text to be shown to users
    """

    user_id = update.effective_user.id

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data is not None:

        lat = str(data["latitude"])
        longi = str(data["longitude"])
        address = data["address"]
        utcOffset = data["utcOffset"]
        star_map_param = data["starmap_preferences"]

        current_date_time = get_current_date_time_string(utcOffset)

        pix = fetch_star_map(lat, longi, address, utcOffset, star_map_param)

        await update.callback_query.message.edit_media(
            media = InputMediaDocument(
                media = pix.tobytes(),
                filename = f"Star_Map_{current_date_time.replace(' ', '_').replace(':', '_')}.png",
                caption = f"Enjoy the stunning stars! Be considerate and leave no trace while stargazing! \n ({current_date_time})"
            ),
            reply_markup = Starmap.REFRESH_BUTTON
        )

        return "Star map updated"
    else:
        await update.callback_query.message.delete()
        return "Please set your location first!"


def fetch_star_map(latitude, longitude, address, utcOffset, preferences):
    """Fetch a star map from skyandtelescope.com.

    Args:
        latitude (str): latitude of the location
        longitude (str): longitude of the location
        address (str): address text of the above location
        utcOffset (int): UTC offset in seconds
        preferences (dict): preferences of the user

    Returns:
        fitz.Pixmap: plane rectangular sets of pixels
    """

    params_inject = {
        "time": int(time.time()*1000), # time.time(): seconds (floating point) since the epoch in UTC
        "latitude": latitude,
        "longitude": longitude,
        "location": address,
        "utcOffset": utcOffset * 1000
    }

    response = requests.get(Starmap.STAR_MAP_BASE_URL, params=params_inject|preferences)    # | to merge two dictionaries
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
