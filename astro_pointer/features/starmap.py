"""
A module consists of functions fetching and forwarding a star map (sky chart) to user

Usage:
Command /starmap is defined by preference_setting_message
"""

import time
import requests
from firebase_admin import db
from requests.models import PreparedRequest
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaDocument, error
from telegram.ext import CallbackContext
import fitz
from astro_pointer.helpers import get_current_date_time_string
from astro_pointer.constants import Starmap


def populate_preference_buttons(user_preferences: dict) -> InlineKeyboardMarkup:
    """Populate the InlineKeyboardMarkup with the current preferences of the user.

    Args:
        user_preferences (dict): The current preferences of the user.

    Returns:
        InlineKeyboardMarkup: The InlineKeyboardMarkup with the current preferences of the user.
    """

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
        text = f"Redscaling {'✔' if user_preferences[Starmap.REDSCALE_DB_KEY] else '❌'}",
        callback_data = Starmap.REDSCALE_CALLBACK_DATA,
    )])

    buttons.append([InlineKeyboardButton(
        text = "Reset to default ↺",
        callback_data = Starmap.RESET_TO_DEFAULT_CALLBACK_DATA
    )])

    buttons.append([InlineKeyboardButton(
        text = "Generate Star Map →",
        callback_data = Starmap.GENERATE_CALLBACK_DATA
    )])

    return InlineKeyboardMarkup(buttons)


async def preference_setting_message(update: Update, context: CallbackContext) -> None:
    """Send a message with the current preferences of the user."""

    args = context.args

    if "skip" in args or "-s" in args:
        await send_star_map(update, context)
        return

    user_id = update.effective_user.id

    ref = db.reference(f"/Users/{user_id}")
    data = ref.get()

    if data is not None:
        await update.message.reply_photo(
            photo = open("assets/star_map_params.png", "rb"),
            caption = "Toggle your star map preferences by clicking the buttons below. They will be saved automatically and used for future star map generation.",
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

    try:
        await update.callback_query.message.edit_reply_markup(
            reply_markup = populate_preference_buttons(Starmap.DEFAULT_PREFERENCES)
        )
    except error.BadRequest:
        pass
    else:
        user_id = update.effective_user.id
        ref = db.reference(f"/Users/{user_id}/starmap_preferences")
        ref.update(Starmap.DEFAULT_PREFERENCES)

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

        lat = data["latitude"]
        longi = data["longitude"]
        address = data["address"]
        utc_offset = data["utc_offset"]
        star_map_param = data["starmap_preferences"]

        current_date_time = get_current_date_time_string(utc_offset)

        star_map_bytes, file_extension = fetch_star_map(lat, longi, address, utc_offset, star_map_param)

        await context.bot.send_document(
            chat_id = chat_id,
            document = star_map_bytes,
            filename = f"Star_Map_{current_date_time.replace(' ', '_').replace(':', '_')}.{file_extension}",
            caption = f"Enjoy the stunning stars! Be considerate and leave no trace while stargazing! \n ({current_date_time})",
            reply_markup = Starmap.REFRESH_BUTTON
        )

    else:
        await context.bot.send_message(
            chat_id = chat_id,
            text = "To get a star map, you need to set a location with /setlocation first."
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

        lat = data["latitude"]
        longi = data["longitude"]
        address = data["address"]
        utc_offset = data["utc_offset"]
        star_map_param = data["starmap_preferences"]

        current_date_time = get_current_date_time_string(utc_offset)

        star_map_bytes, file_extension = fetch_star_map(lat, longi, address, utc_offset, star_map_param)

        await update.callback_query.message.edit_media(
            media = InputMediaDocument(
                media = star_map_bytes,
                filename = f"Star_Map_{current_date_time.replace(' ', '_').replace(':', '_')}.{file_extension}",
                caption = f"Enjoy the stunning stars! Be considerate and leave no trace while stargazing! \n ({current_date_time})"
            ),
            reply_markup = Starmap.REFRESH_BUTTON
        )

        return "Star map updated"

    await update.callback_query.message.delete()
    return "To get a star map, set a location with /setlocation first."


def fetch_star_map(latitude: float, longitude: float, address: str, utc_offset: int, preferences: dict):
    """Fetch a star map from skyandtelescope.com.

    Args:
        latitude (float): latitude of the location
        longitude (float): longitude of the location
        address (str): address text of the above location
        utc_offset (int): UTC offset in seconds
        preferences (dict): preferences of the user

    Returns:
        bytes or str: bytes object of a plane rectangular sets of pixels or a URL string
        str: file extension of the image
    """

    params_inject = {
        "time": int(time.time()*1000),  # time.time(): seconds (floating point) since the epoch in UTC
        "latitude": latitude,
        "longitude": longitude,
        "location": address,
        "utcOffset": utc_offset * 1000  # convert to milliseconds
    }

    redscale = preferences.pop(Starmap.REDSCALE_DB_KEY, False)

    if redscale:
        response = requests.get(Starmap.STAR_MAP_BASE_URL, params=params_inject|preferences)    # | to merge two dictionaries
        with fitz.open(stream=response.content) as doc:
            page = doc.load_page(0)  # load the first page
            pix = page.get_pixmap(
                dpi = 200,
                colorspace = fitz.csRGB,
                annots = False,
                clip = fitz.IRect(1, 1, 600, 650)
            )
            pix.tint_with(black=-129010, white=0) # no idea on how these values work, just do trial and error

        return pix.tobytes(), "png"

    req = PreparedRequest()
    req.prepare_url(url=Starmap.STAR_MAP_BASE_URL, params=params_inject|preferences)
    return req.url, "pdf"   # TODO: rename the file
