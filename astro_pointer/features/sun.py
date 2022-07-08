"""
A module that consists of functions fetching and displaying near-real-time sun photos from NASA.

Usage:
Command /sun is defined by send_sun_photo
"""

import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, error
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from astro_pointer.helpers import get_current_date_time_string
from astro_pointer.constants import Sun


async def fetch_sun_photos(context: CallbackContext) -> None:
    """Fetch all the sun photos from the server every 15 mins."""

    async with httpx.AsyncClient() as client:
        tasks = (client.get(url) for url in Sun.PHOTO_URLS)
        reqs = await asyncio.gather(*tasks)

    for i, r in enumerate(reqs):
        with open(f"{Sun.PHOTO_PATH}{i}.jpg", "wb") as f:
            f.write(r.content)

    with open(f"{Sun.PHOTO_PATH}log.txt", "w") as txt:
        txt.write(f"{get_current_date_time_string(0)} UTC")   # UTC time


def populate_keyboard_buttons(sun_number: int, show_description_button: bool) -> InlineKeyboardMarkup:
    """Populate the keyboard buttons.

    Args:
        sun_number (int): the index of the sun photo
        show_description_button (bool):
            True to display 'Show description', False to display 'Hide description'

    Returns:
        InlineKeyboardMarkup: the keyboard buttons
    """

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("<<", callback_data=f"{Sun.UPDATE_PHOTO}_{(sun_number - 1) % Sun.PHOTO_COUNT}"),
            InlineKeyboardButton("↻", callback_data=f"{Sun.UPDATE_PHOTO}_{sun_number}"),
            InlineKeyboardButton(">>", callback_data=f"{Sun.UPDATE_PHOTO}_{(sun_number + 1) % Sun.PHOTO_COUNT}")
        ],
        [
            InlineKeyboardButton(
                text = f"{'⇣ Show' if show_description_button else '⇡ Hide'} description",
                callback_data = f"{Sun.SHOW_DESCRIPTION if show_description_button else Sun.HIDE_DESCRIPTION}_{sun_number}"
            )
        ]
    ])


async def sun_subscription(context: CallbackContext) -> None:
    await send_sun_photo(update=None, context=context)


async def send_sun_photo(update: Update, context: CallbackContext) -> None:
    """Send a photo of the current sun."""

    chat_id = context.job.chat_id if update is None else update.effective_chat.id

    with open(f"{Sun.PHOTO_PATH}log.txt", 'r') as txt:
        last_fetched = txt.read()
    default_starting_point = 0

    with open(f"{Sun.PHOTO_PATH}{default_starting_point}.jpg", "rb") as pic:
        await context.bot.send_photo(
            chat_id = chat_id,
            photo = pic,
            caption = (f"🌞 Live Photos of the Sun \n"
                        f"{Sun.PHOTO_NAMES[default_starting_point]} \n"
                        f"({last_fetched})"),
            reply_markup = populate_keyboard_buttons(default_starting_point, True)
        )


async def show_description(update: Update, context: CallbackContext) -> str:
    """Expand the message to show the description.

    Returns:
        str: status
    """

    sun_number = int(update.callback_query.data[len(Sun.SHOW_DESCRIPTION)+1:])

    await update.callback_query.message.edit_caption(
        caption = (f"{update.callback_query.message.caption} \n"
                    "************************************ \n"
                    f"{Sun.PHOTO_DESCRIPTIONS[sun_number]}"),
        parse_mode = ParseMode.HTML,
        reply_markup = populate_keyboard_buttons(sun_number, False)
    )

    return "Description shown"


async def hide_description(update: Update, context: CallbackContext) -> str:
    """Collapse the message and remove the description part.

    Returns:
        str: status
    """

    sun_number = int(update.callback_query.data[len(Sun.HIDE_DESCRIPTION)+1:])

    await update.callback_query.message.edit_caption(
        caption = (f"{update.callback_query.message.caption[:update.callback_query.message.caption.find('*')]}"),
        reply_markup = populate_keyboard_buttons(sun_number, True)
    )
    return "Description hidden"


async def update_sun_photo(update: Update, context: CallbackContext) -> str:
    """Cycle through the sun photo list or refresh the current one.

    Returns:
        str: status
    """

    sun_number = int(update.callback_query.data[len(Sun.UPDATE_PHOTO)+1:])
    with open(f"{Sun.PHOTO_PATH}log.txt", 'r') as txt:
        last_fetched = txt.read()

    try:
        with open(f"{Sun.PHOTO_PATH}{sun_number}.jpg", "rb") as pic:
            await update.callback_query.message.edit_media(
                media = InputMediaPhoto(
                    media = pic,
                    caption = (f"🌞 Live Photos of the Sun \n"
                                f"{Sun.PHOTO_NAMES[sun_number]} \n"
                                f"({last_fetched})")
                ),
                reply_markup = populate_keyboard_buttons(sun_number, True)
            )

    except error.BadRequest:
        return "The photo is up-to-date. Please try again later."
    else:
        return "Sun photo refreshed"
