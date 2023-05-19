"""
This file consists of miscellaneous features of the bot.

"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from astro_pointer.constants import COMMAND_DESCRIPTIONS, TUTORIAL_TEXT, COMMAND_KEYBOARD


async def show_credits(update: Update, context: CallbackContext) -> None:
    """Display the data source of the star map and a link to this GitHub repo."""

    await update.message.reply_text(
        text = ("Star map is made available to you by skyandtelescope.org. \n"
                "Astronomical and weather data are provided by WeatherAPI.com. \n"
                "Courtesy of NASA/SDO and the AIA, EVE, and HMI science teams for the near-real-time (NRT) images. \n"),
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Visit skyandtelescope.org", url="https://skyandtelescope.org/")],
            [InlineKeyboardButton("Follow this project on GitHub", url="https://github.com/ChoiTommy/astro-pointer-bot")]
        ])
    )


async def bot_tutorial(update: Update, context: CallbackContext) -> None:   # TODO: privacy policy
    """Act as a welcome message and tutorial to anyone who starts the bot"""

    with open("assets/description_pic.png", "rb") as pic:
        await update.message.reply_photo(
            photo = pic,
            caption = TUTORIAL_TEXT,
            parse_mode = ParseMode.HTML,
            reply_markup = COMMAND_KEYBOARD
        )

async def show_commands(update: Update, context: CallbackContext) -> None:
    """Display the list of commands"""

    await update.message.reply_text(
        text = COMMAND_DESCRIPTIONS,
        parse_mode = ParseMode.HTML
    )
    