# https://www.epochconverter.com/
# https://nominatim.org/release-docs/develop/api/Reverse/

# TODO pdf to image, red scale img, star map features toggles, show moon phases, etc.
import misc, userinfo, settings, starmap, astrodata, weather

import logging
import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO
)
logger = logging.getLogger(__name__)

# Load credentials from enviroment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register a command handler
    dispatcher.add_handler(CommandHandler("credits", misc.show_credits))
    dispatcher.add_handler(CommandHandler("starmap", starmap.send_star_map))
    dispatcher.add_handler(CommandHandler("myinfo", userinfo.show_user_info))
    dispatcher.add_handler(CommandHandler("deletemyinfo", userinfo.delete_user_info)) # request for confirmation before proceeding
    dispatcher.add_handler(CommandHandler("astrodata", astrodata.show_astro_data))
    dispatcher.add_handler(CommandHandler("weather", weather.show_weather_data))

    dispatcher.add_handler(ConversationHandler(
        entry_points = [CommandHandler("setlocation", settings.set_location)],
        states = {
            0: [MessageHandler(Filters.location, settings.update_location)]
        },
        fallbacks = [CommandHandler("cancel", settings.cancel)],
        conversation_timeout = 120 # 2 mins
    ))

    # Start the Bot using polling
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()