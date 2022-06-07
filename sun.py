"""
sun is a module that consists of functions fetching and displaying near-real-time sun images from NASA.

Usage:
Command /sun is defined by send_sun_pic
"""

import helpers
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, error
from telegram.ext import CallbackContext


SUN_PIC_URLS = [  # 19 images, indices from 0..18
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg",          # AIA 193 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0304.jpg",          # AIA 304 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0171.jpg",          # AIA 171 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0211.jpg",          # AIA 211 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0131.jpg",          # AIA 131 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0335.jpg",          # AIA 335 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0094.jpg",          # AIA 094 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_1600.jpg",          # AIA 1600 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_1700.jpg",          # AIA 1700 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_211193171.jpg",     # AIA 211 Å, 193 Å, 171 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/f_304_211_171_1024.jpg",        # AIA 304 Å, 211 Å, 171 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/f_094_335_193_1024.jpg",        # AIA 094 Å, 335 Å, 193 Å
    "https://sdo.gsfc.nasa.gov/assets/img/latest/f_HMImag_171_1024.jpg",         # AIA 171 Å & HMIB
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIB.jpg",          # HMI Magnetogram
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIBC.jpg",         # HMI Colorized Magnetogram
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg",         # HMI Intensitygram - colored <- starting point
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIF.jpg",         # HMI Intensitygram - Flattened
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMII.jpg",          # HMI Intensitygram
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMID.jpg"           # HMI Dopplergram
]

SUN_PIC_NAMES = [
    "AIA 193 Å",
    "AIA 304 Å",
    "AIA 171 Å",
    "AIA 211 Å",
    "AIA 131 Å",
    "AIA 335 Å",
    "AIA 094 Å",
    "AIA 1600 Å",
    "AIA 1700 Å",
    "AIA 211 Å, 193 Å, 171 Å",
    "AIA 304 Å, 211 Å, 171 Å",
    "AIA 094 Å, 335 Å, 193 Å",
    "AIA 171 Å & HMIB",
    "HMI Magnet ogram",
    "HMI Colorized Magnetogram",
    "HMI Intensitygram - colored",
    "HMI Intensitygram - Flattened",
    "HMI Intensitygram",
    "HMI Dopplergram",
]


async def send_sun_pic(update: Update, context: CallbackContext) -> None:
    """Send a picture of the currnet sun"""

    current_date_time = helpers.get_current_date_time_string(0) # UTC time

    default_starting_point = 15

    await update.message.reply_photo(
        photo = SUN_PIC_URLS[default_starting_point] + f"?a={int(time.time()/900)}",  # new url in ~ every 15 mins
        caption = (f"{default_starting_point+1}. {SUN_PIC_NAMES[default_starting_point]} \n"
                    f"(Last refreshed: \n{current_date_time} UTC)"),
        reply_markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton("<<", callback_data=f"SUN_{default_starting_point-1}"), InlineKeyboardButton(">>", callback_data=f"SUN_{default_starting_point+1}")],
                            [InlineKeyboardButton("Refresh current image", callback_data=f"SUN_{default_starting_point}")]
                        ])
    )


async def update_sun_pic(update: Update, context: CallbackContext) -> str:
    """Update the sun picture"""

    sun_number = int(update.callback_query.data[4:])

    current_date_time = helpers.get_current_date_time_string(0) # UTC time

    try:
        msg = await update.callback_query.message.edit_media(
            media = InputMediaPhoto(media=(SUN_PIC_URLS[sun_number] + f"?a={int(time.time()/900)}"))
        )
        await msg.edit_caption(
            caption = (f"{sun_number+1}. {SUN_PIC_NAMES[sun_number]} \n"
                        f"(Last refreshed: \n{current_date_time} UTC)"),
            reply_markup = InlineKeyboardMarkup([
                                [InlineKeyboardButton("<<", callback_data=f"SUN_{(sun_number - 1) % 19}"), InlineKeyboardButton(">>", callback_data=f"SUN_{(sun_number + 1) % 19}")],
                                [InlineKeyboardButton("Refresh current image", callback_data=f"SUN_{sun_number}")]
                            ])
        )
    except error.TimedOut:
        return "An error has occurred. Please try again."
    else:
        return "Sun pic refreshed"
