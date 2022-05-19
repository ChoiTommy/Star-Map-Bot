"""
constants is a module that consists of all the constants used in this bot.

"""
import os
from dotenv import load_dotenv


# Load credentials from environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# dict for getting the corresponding moon phase emojis
MOON_PHASE_DICT = {
    "New Moon" : "🌑",
    "Waxing Crescent" : "🌒",
    "First Quarter" : "🌓",
    "Waxing Gibbous" : "🌔",
    "Full Moon" : "🌕",
    "Waning Gibbous" : "🌖",
    "Last Quarter" : "🌗",
    "Waning Crescent" : "🌘"
}