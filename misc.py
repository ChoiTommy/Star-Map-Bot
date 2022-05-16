"""
misc is a module that consists of miscellaneous functions not relating to the main features of the bot.

Usage:
Command /credits is defined by show_credits
Command /start is defined by bot_tutorial
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext

async def show_credits(update: Update, context: CallbackContext) -> None:
    """Display the data source of the star map and a link to this GitHub repo."""

    await update.message.reply_text(
        text = ("Star map is made available to you by skyandtelescope.org. "
                "Astronomical and weather data are provided by WeatherAPI.com. "
                "Visit their website for more information. "
        ),
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Visit skyandtelescope.org", url="https://skyandtelescope.org/")],
            [InlineKeyboardButton("Check out their interactive sky chart", url="https://skyandtelescope.org/interactive-sky-chart/")],
            [InlineKeyboardButton("Follow this project on GitHub", url="https://github.com/ChoiTommy/Star-Map-Bot")]
        ])
    )


TUTORIAL_TEXT = f"""
@star_map_bot is designed with mobile devices in mind.

@star_map_bot is an easy-to-use stargazing bot that provides you with all the necessary stargazing information including star maps (sky charts), weather and astronomical data, etc.

To get the most out of this bot, you are required to set a location (/setlocation). This location data is used for generating star maps, displaying weather and astronomical data at that specific location only. Users can delete their data at anytime with the command /deletemyinfo.

As weather and astronomical data do not differ much within few kilometers' range, feel free to turn off 'Precise Location' (on iOS) for Telegram in Settings. When setting up you location, you can move the map around in the Telegram app to provide a location wherever you want too.

Press the menu button at the bottom left of your screen to view all the commands available.
"""


async def bot_tutorial(update: Update, context: CallbackContext) -> None: # TODO: privacy policy
    """Act as a welcome message and tutorial to anyone who starts the bot"""

    await update.message.reply_text(
        text = TUTORIAL_TEXT,
        parse_mode = ParseMode.HTML
    )