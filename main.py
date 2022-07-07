"""
@AstroPointerBot is an easy-to-use astronomical bot that provides you with
all the necessary stargazing information including star maps (sky
charts), weather and astronomical data, etc.

Usage:
Send /start to get a welcome message from the bot.
Send /setlocation to set your location to enable the the core features.
Send /starmap to get a star map pdf at the location set.
Send /astrodata to get a list of astronomical data at the location set.
Send /sun to view a series of sun photos in various wavelengths.
Send /weather to get a weather report at the location set.
Send /iss to get the live location of the International Space Station.
Send /myinfo to view the data associate with you stored on the server.
Send /deletemyinfo to purge you data permanently on the server.
Send /credits to view the data sources of all the information this bot provides.
Send /cancel to halt any operations.
"""

# TODO API request async, astronomy news rss
import logging
import firebase_admin
from firebase_admin import credentials
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from astro_pointer import misc, userinfo, callback_queries
from astro_pointer.constants import BOT_TOKEN, DATABASE_URL, GOOGLE_APPLICATION_CREDENTIALS
from astro_pointer.features import (
    starmap,
    astrodata,
    weather,
    sun,
    iss,
    subscription
)


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point of the script."""

    cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
    firebase_admin.initialize_app(
        credential = cred,
        options = {
            "databaseURL" : DATABASE_URL
        }
    )

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Pushing jobs into the job queue
    application.job_queue.run_once(subscription.load_jobs_into_jobqueue, when=1)        # 1 second from now
    application.job_queue.run_repeating(sun.fetch_sun_photos, interval=900, first=2)    # 900s = 15 mins, do almost immediately

    # Register command handlers
    application.add_handler(CommandHandler("start", misc.bot_tutorial))
    application.add_handler(CommandHandler("credits", misc.show_credits))
    application.add_handler(CommandHandler("starmap", starmap.preference_setting_message))
    application.add_handler(CommandHandler("myinfo", userinfo.show_user_info))
    application.add_handler(CommandHandler("astrodata", astrodata.show_astro_data))
    application.add_handler(CommandHandler("weather", weather.show_weather_data))
    application.add_handler(CommandHandler("sun", sun.send_sun_photo))
    application.add_handler(CommandHandler("iss", iss.iss_live_location, block=False))
    application.add_handler(CommandHandler(["subscribe", "sub"], subscription.subscribe))
    application.add_handler(CommandHandler(["unsubscribe", "unsub"], subscription.unsubscribe))

    application.add_handler(ConversationHandler(
        entry_points = [CommandHandler("setlocation", userinfo.set_location)],
        states = {
            0: [MessageHandler(
                filters.LOCATION | filters.Regex("[0-9]*\.[0-9]+,[ ]?[0-9]*\.[0-9]+"),
                userinfo.update_location
            )]
        },
        fallbacks = [CommandHandler("cancel", userinfo.cancel_location_setup)],
        conversation_timeout = 300 # 5 mins
    ))

    application.add_handler(ConversationHandler(
        entry_points = [CommandHandler("deletemyinfo", userinfo.deletion_confirmation)],
        states = {
            0: [MessageHandler(filters.Regex("^(Yes|No)$"), userinfo.delete_user_info)]
        },
        fallbacks = [CommandHandler("cancel", userinfo.cancel_deletion)],
        conversation_timeout = 300
    ))

    application.add_handler(CallbackQueryHandler(callback_queries.callback))

    # Start the Bot using polling
    application.run_polling()


if __name__ == "__main__":
    main()
