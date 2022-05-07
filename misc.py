from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext

def show_credits(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text = "Star map is made available to you by skyandtelescope.org. This bot is not affiliated with skyandtelescope.org. Visit their website for more information.",
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Visit skyandtelescope.org", url="https://skyandtelescope.org/")],
            [InlineKeyboardButton("Check out their interactive sky chart", url="https://skyandtelescope.org/interactive-sky-chart/")]
        ])
    )