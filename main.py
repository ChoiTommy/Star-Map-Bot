"""
@star_map_bot is an easy-to-use stargazing bot that provides you with
all the necessary stargazing information including star maps (sky
charts), weather and astronomical data, etc.

Usage:
Send /start to get a welcome message from the bot.
Send /setlocation to set your location to enable the the core features.
Send /starmap to get a star map pdf at the location set.
Send /astrodata to get a list of astronomical data at the location set.
Send /weather to get a weather report at the location set.
Send /myinfo to view the data associate with you stored on the server.
Send /deletemyinfo to purge you data permanently on the server.
Send /credits to view the data sources of all the infomation this bot provides.
Send /cancel to halt any operations.
"""

# TODO API request async, star map features toggles, astronomy news rss, subscriber (send info actively to subscribed users)
import misc, userinfo, starmap, astrodata, weather, sun, constants, callback_queries

import logging
import firebase_admin
from firebase_admin import credentials
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, Filters


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point of the script."""

    cred = credentials.Certificate(constants.GOOGLE_APPLICATION_CREDENTIALS)
    firebase_admin.initialize_app(
        credential = cred,
        options = {
            "databaseURL" : constants.DATABASE_URL
        }
    )

    # Create the Updater and pass it your bot's token.
    updater = Updater(constants.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", misc.bot_tutorial))
    dispatcher.add_handler(CommandHandler("credits", misc.show_credits))
    dispatcher.add_handler(CommandHandler("starmap", starmap.send_star_map))
    dispatcher.add_handler(CommandHandler("myinfo", userinfo.show_user_info))
    dispatcher.add_handler(CommandHandler("astrodata", astrodata.show_astro_data))
    dispatcher.add_handler(CommandHandler("weather", weather.show_weather_data))
    dispatcher.add_handler(CommandHandler("sun", sun.send_sun_pic))

    dispatcher.add_handler(ConversationHandler(
        entry_points = [CommandHandler("setlocation", userinfo.set_location)],
        states = {
            0: [MessageHandler(Filters.location, userinfo.update_location)]
        },
        fallbacks = [CommandHandler("cancel", userinfo.cancel_location_setup)],
        conversation_timeout = 300 # 5 mins
    ))

    dispatcher.add_handler(ConversationHandler(
        entry_points = [CommandHandler("deletemyinfo", userinfo.deletion_confirmation)],
        states = {
            0: [MessageHandler(Filters.regex("^(Yes|No)$"), userinfo.delete_user_info)]
        },
        fallbacks = [CommandHandler("cancel", userinfo.cancel_deletion)],
        conversation_timeout = 300
    ))

    dispatcher.add_handler(CallbackQueryHandler(callback_queries.callback))

    # Start the Bot using polling
    updater.start_polling()

    # Start listening to webhook
    # updater.start_webhook(listen = "0.0.0.0",
    #                   port = constants.PORT,
    #                   url_path = constants.BOT_TOKEN,
    #                   webhook_url = "https://star-map-bot.herokuapp.com/" + constants.BOT_TOKEN)
    updater.idle()


if __name__ == "__main__":
    main()