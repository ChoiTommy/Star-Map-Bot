"""
A module that consists of functions fetching and displaying near-real-time sun photos from NASA.

Usage:
Command /sun is defined by send_sun_photo

TODO separate out sun data to a new file
"""

from helpers import get_current_date_time_string
from constants import (
    UPDATE_SUN_PHOTO,
    SHOW_SUN_DESCRIPTION,
    HIDE_SUN_DESCRIPTION,
    SUN_PHOTO_URLS,
    SUN_PHOTO_COUNT,
    SUN_PHOTO_NAMES,
    SUN_PHOTO_DESCRIPTIONS,
    SUN_PHOTO_PATH          # contains x.jpg or log.txt
)
import time, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, error
from telegram.ext import CallbackContext
from telegram.constants import ParseMode


async def fetch_sun_photos(context: CallbackContext) -> None: # Possibility to switch to asynchronous?
    """Fetch all the sun photos from the server. This is run every 15 mins."""

    for i in range(len(SUN_PHOTO_URLS)):
        img_data = requests.get(SUN_PHOTO_URLS[i], stream=True).content
        with open(f"{SUN_PHOTO_PATH}{i}.jpg", "wb") as f:
            f.write(img_data)

    with open(f"{SUN_PHOTO_PATH}log.txt", "w") as txt:
        txt.write(f"{get_current_date_time_string(0)} UTC")   # UTC time


async def send_sun_photo(update: Update, context: CallbackContext) -> None:
    """Send a photo of the current sun."""

    with open(f"{SUN_PHOTO_PATH}log.txt", 'r') as txt:
        last_fetched = txt.read()
    default_starting_point = 0

    await update.message.reply_photo(
        photo = open(f"{SUN_PHOTO_PATH}{default_starting_point}.jpg", "rb"),
        caption = (f"🌞 Live Photos of the Sun \n"
                    f"{SUN_PHOTO_NAMES[default_starting_point]} \n"
                    f"({last_fetched})"),
        reply_markup = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("<<", callback_data=f"{UPDATE_SUN_PHOTO}_{(default_starting_point - 1) % SUN_PHOTO_COUNT}"),
                                InlineKeyboardButton("↻", callback_data=f"{UPDATE_SUN_PHOTO}_{default_starting_point}"),
                                InlineKeyboardButton(">>", callback_data=f"{UPDATE_SUN_PHOTO}_{(default_starting_point + 1) % SUN_PHOTO_COUNT}")
                            ],
                            [InlineKeyboardButton("⇣ Show description", callback_data=f"{SHOW_SUN_DESCRIPTION}_{default_starting_point}")]
                        ])
    )


async def show_description(update: Update, context: CallbackContext) -> str:
    """Expand the message to show the description.

    Returns:
        str: status
    """

    sun_number = int(update.callback_query.data[len(SHOW_SUN_DESCRIPTION)+1:])

    await update.callback_query.message.edit_caption(
        caption = (f"{update.callback_query.message.caption} \n"
                    "************************************ \n"
                    f"{SUN_PHOTO_DESCRIPTIONS[sun_number]}"),
        parse_mode = ParseMode.HTML,
        reply_markup = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("<<", callback_data=f"{UPDATE_SUN_PHOTO}_{(sun_number - 1) % SUN_PHOTO_COUNT}"),
                                InlineKeyboardButton("↻", callback_data=f"{UPDATE_SUN_PHOTO}_{sun_number}"),
                                InlineKeyboardButton(">>", callback_data=f"{UPDATE_SUN_PHOTO}_{(sun_number + 1) % SUN_PHOTO_COUNT}")
                            ],
                            [InlineKeyboardButton("⇡ Hide description", callback_data=f"{HIDE_SUN_DESCRIPTION}_{sun_number}")]
                        ])
    )
    return "Description shown"


async def hide_description(update: Update, context: CallbackContext) -> str:
    """Collapse the message and remove the description part.

    Returns:
        str: status
    """

    sun_number = int(update.callback_query.data[len(HIDE_SUN_DESCRIPTION)+1:])

    await update.callback_query.message.edit_caption(
        caption = (f"{update.callback_query.message.caption[:update.callback_query.message.caption.find('*')]}"),
        reply_markup = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("<<", callback_data=f"{UPDATE_SUN_PHOTO}_{(sun_number - 1) % SUN_PHOTO_COUNT}"),
                                InlineKeyboardButton("↻", callback_data=f"{UPDATE_SUN_PHOTO}_{sun_number}"),
                                InlineKeyboardButton(">>", callback_data=f"{UPDATE_SUN_PHOTO}_{(sun_number + 1) % SUN_PHOTO_COUNT}")
                            ],
                            [InlineKeyboardButton("⇣ Show description", callback_data=f"{SHOW_SUN_DESCRIPTION}_{sun_number}")]
                        ])
    )
    return "Description hidden"


async def update_sun_photo(update: Update, context: CallbackContext) -> str:
    """Cycle through the sun photo list or refresh the current one.

    Returns:
        str: status
    """

    sun_number = int(update.callback_query.data[len(UPDATE_SUN_PHOTO)+1:])
    with open(f"{SUN_PHOTO_PATH}log.txt", 'r') as txt:
        last_fetched = txt.read()

    try:
        await update.callback_query.message.edit_media(
            media = InputMediaPhoto(
                media = open(f"{SUN_PHOTO_PATH}{sun_number}.jpg", "rb"),
                caption = (f"🌞 Live Photos of the Sun \n"
                            f"{SUN_PHOTO_NAMES[sun_number]} \n"
                            f"({last_fetched})")
            ),
            reply_markup = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("<<", callback_data=f"{UPDATE_SUN_PHOTO}_{(sun_number - 1) % SUN_PHOTO_COUNT}"),
                                    InlineKeyboardButton("↻", callback_data=f"{UPDATE_SUN_PHOTO}_{sun_number}"),
                                    InlineKeyboardButton(">>", callback_data=f"{UPDATE_SUN_PHOTO}_{(sun_number + 1) % SUN_PHOTO_COUNT}")
                                ],
                                [InlineKeyboardButton("⇣ Show description", callback_data=f"{SHOW_SUN_DESCRIPTION}_{sun_number}")]
                            ])
        )
    except error.BadRequest:
        return "The photo is up-to-date. Please try again later."
    else:
        return "Sun photo refreshed"
