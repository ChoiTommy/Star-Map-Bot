"""
A module consists of all the constants used in this bot

"""

import os
# from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# Load credentials from environment variables
# load_dotenv()


# main.py
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
DATABASE_URL = os.getenv("DATABASE_URL")


# Star Map
class Starmap:
    STAR_MAP_BASE_URL = "https://www.heavens-above.com/SkyAndTelescope/StSkyChartPDF.ashx"
    REST_OF_THE_STAR_MAP_PARAM = { # params to be injected: time, latitude, longitude, location, utcOffset(in ms)
        "showEquator": False,
        "showEcliptic": True,
        "showStarNames": False,
        "showPlanetNames": True,
        "showConsNames": True,
        "showConsLines": True,
        "showConsBoundaries": False,
        "showSpecials": False,
        "use24hClock": True
    }
    REFRESH_CALLBACK_DATA = "REFRESH_STARMAP"
    REFRESH_BUTTON = InlineKeyboardMarkup([
        [InlineKeyboardButton("↻ Refresh", callback_data=REFRESH_CALLBACK_DATA)]
    ])
    PREFERENCE_CALLBACK_DATA = "PREF_STAR_MAP"
    GENERATE_CALLBACK_DATA = "GENERATE_STAR_MAP"


# Astrodata
class Astrodata:
    API_BASE_URL = "https://api.weatherapi.com/v1/astronomy.json"
    API_KEY = os.getenv("WEATHER_API_KEY")
    MOON_PHASE_DICT = {             # dict for getting the corresponding moon phase emojis
        "New Moon" : "🌑",
        "Waxing Crescent" : "🌒",
        "First Quarter" : "🌓",
        "Waxing Gibbous" : "🌔",
        "Full Moon" : "🌕",
        "Waning Gibbous" : "🌖",
        "Third Quarter" : "🌗",
        "Waning Crescent" : "🌘"
    }
    REFRESH_CALLBACK_DATA = "REFRESH_ASTRODATA"
    REFRESH_BUTTON = InlineKeyboardMarkup([
                                [InlineKeyboardButton("↻ Refresh", callback_data=REFRESH_CALLBACK_DATA)]
                            ])


# Weather
class Weather:
    API_KEY = Astrodata.API_KEY
    API_BASE_URL = "https://api.weatherapi.com/v1/current.json"
    REFRESH_CALLBACK_DATA = "REFRESH_WEATHER"
    REFRESH_BUTTON = InlineKeyboardMarkup([
                                [InlineKeyboardButton("↻ Refresh", callback_data=REFRESH_CALLBACK_DATA)]
                            ])


# Sun
class Sun:
    UPDATE_PHOTO = "SUN"
    SHOW_DESCRIPTION = "SHOW"
    HIDE_DESCRIPTION = "HIDE"
    PHOTO_URLS = [  # 19 photos, indices from 0..18
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
        "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg",         # HMI Intensitygram - colored
        "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIF.jpg",         # HMI Intensitygram - Flattened
        "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMII.jpg",          # HMI Intensitygram
        "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMID.jpg"           # HMI Dopplergram
    ]
    PHOTO_COUNT = len(PHOTO_URLS)
    PHOTO_NAMES = [
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
        "HMI Magnetogram",
        "HMI Colorized Magnetogram",
        "HMI Intensitygram - colored",
        "HMI Intensitygram - Flattened",
        "HMI Intensitygram",
        "HMI Dopplergram",
    ]
    PHOTO_DESCRIPTIONS = [
        # 193
        "This channel highlights the outer atmosphere of the Sun - called the corona - as well as hot flare plasma. Hot active regions, solar flares, and coronal mass ejections will appear bright here. The dark areas - called coronal holes - are places where very little radiation is emitted, yet are the main source of solar wind particles.\n\n<strong>Where:</strong> Corona and hot flare plasma\n<strong>Wavelength:</strong>  193 angstroms (0.0000000193 m) = Extreme Ultraviolet\n<strong>Primary ions seen:</strong> 11 times ionized iron (Fe XII)\n<strong>Characteristic temperature:</strong> 1.25 million K (2.25 million F)",
        # 304
        "This channel is especially good at showing areas where cooler dense plumes of plasma (filaments and prominences) are located above the visible surface of the Sun. Many of these features either can't be seen or appear as dark lines in the other channels. The bright areas show places where the plasma has a high density.\n\n<strong>Where:</strong> Upper chromosphere and lower transition region\n<strong>Wavelength:</strong> 304 angstroms (0.0000000304 m) = Extreme Ultraviolet\n<strong>Primary ions seen:</strong> singly ionized helium (He II)\n<strong>Characteristic temperature:</strong> 50,000 K (90,000 F)",
        # 171
        "This channel is especially good at showing coronal loops - the arcs extending off of the Sun where plasma moves along magnetic field lines. The brightest spots seen here are locations where the magnetic field near the surface is exceptionally strong.\n\n<strong>Where:</strong> Quiet corona and upper transition region\n<strong>Wavelength:</strong> 171 angstroms (0.0000000171 m) = Extreme Ultraviolet\n<strong>Primary ions seen:</strong>  8 times ionized iron (Fe IX)\n<strong>Characteristic temperature:</strong> 1 million K (1.8 million F)",
        # 211
        "This channel (as well as AIA 335) highlights the active region of the outer atmosphere of the Sun - the corona. Active regions, solar flares, and coronal mass ejections will appear bright here. The dark areas - called coronal holes - are places where very little radiation is emitted, yet are the main source of solar wind particles.\n\n<strong>Where:</strong> Active regions of the corona\n<strong>Wavelength:</strong>  211 angstroms (0.0000000211 m) = Extreme Ultraviolet\n<strong>Primary ions seen:</strong> 13 times ionized iron (Fe XIV)\n<strong>Characteristic temperature:</strong> 2 million K (3.6 million F)",
        # 131
        "This channel (as well as AIA 094) is designed to study solar flares. It measures extremely hot temperatures around 10 million K (18 million F), as well as cool plasmas around 400,000 K (720,000 F). It can take images every 2 seconds (instead of 10) in a reduced field of view in order to look at flares in more detail.\n\n<strong>Where:</strong> Flaring regions of the corona\n<strong>Wavelength:</strong>  131 angstroms (0.0000000131 m) = Extreme Ultraviolet\n<strong>Primary ions seen:</strong>  20 and 7 times ionized iron (Fe VIII, Fe XXI)\n<strong>Characteristic temperatures:</strong> 10 million K (18 million F)",
        # 335
        "This channel (as well as AIA 211) highlights the active region of the outer atmosphere of the Sun - the corona. Active regions, solar flares, and coronal mass ejections will appear bright here. The dark areas - or coronal holes - are places where very little radiation is emitted, yet are the main source of solar wind particles.\n\n<strong>Where:</strong> Active regions of the corona\n<strong>Wavelength:</strong>  335 angstroms (0.0000000335 m) = Extreme Ultraviolet\n<strong>Primary ions seen:</strong> 15 times ionized iron (Fe XVI)\n<strong>Characteristic temperature:</strong> 2.8 million K (5 million F)",
        # 094
        "This channel (as well as AIA 131) is designed to study solar flares. It measures extremely hot temperatures around 6 million Kelvin (10.8 million F). It can take images every 2 seconds (instead of 10) in a reduced field of view in order to look at flares in more detail.\n\n<strong>Where:</strong> Flaring regions of the corona\n<strong>Wavelength:</strong>  94 angstroms (0.0000000094 m) = Extreme Ultraviolet/soft X-rays\n<strong>Primary ions seen:</strong>  17 times ionized iron (Fe XVIII)\n<strong>Characteristic temperature:</strong> 6 million K (10.8 million F)",
        # 1600
        "This channel (as well as AIA 1700) often shows a web-like pattern of bright areas that highlight places where bundles of magnetic fields lines are concentrated. However, small areas with a lot of field lines will appear black, usually near sunspots and active regions.\n\n<strong>Where:</strong> Transition region and upper photosphere\n<strong>Wavelength:</strong>  1600 angstroms (0.00000016 m) = Far Ultraviolet\n<strong>Primary ions seen:</strong>  thrice ionized carbon (C IV) and Continuum\n<strong>Characteristic temperatures:</strong> 6,000 K (11,000 F), and 100,000 K (180,000 F)",
        # 1700
        "This channel (as well as AIA 1600) often shows a web-like pattern of bright areas that highlight places where bundles of magnetic fields lines are concentrated. However, small areas with a lot of field lines will appear black, usually near sunspots and active regions.\n\n<strong>Where:</strong> Temperature minimum and photosphere\n<strong>Wavelength:</strong> 1700 angstroms (0.00000017 m) = Far Ultraviolet\n<strong>Primary ions seen:</strong> Continuum\n<strong>Characteristic temperature:</strong> 6,000 K (11,000 F)",
        # 211, 193, 171
        "This image combines three images with different, but very similar, temperatures. The colors are assigned differently than in the single images. Here AIA 211 is red, AIA 193 is green, and AIA 171 is blue.  Each highlights a different part of the corona.",
        # 304, 211, 171
        "This image combines three images with quite different temperatures. The colors are assigned differently than in the single images. Here AIA 304 is red (showing the chromosphere), AIA 211 is green (corona), and AIA 171 is dark blue (corona).",
        # 094, 335, 193
        "This image combines three images with different temperatures. Each image is assigned a color, and they are not the same used in the single images. Here AIA 094 is red, AIA 335 is green, and AIA 193 is blue.  Each highlights a different part of the corona.",
        # 171, HMIB
        "This channel is especially good at showing coronal loops - the arcs extending off of the Sun where plasma moves along magnetic field lines. The brightest spots seen here are locations where the magnetic field near the surface is exceptionally strong.\n\n<strong>Where:</strong> Quiet corona and upper transition region\n<strong>Wavelength:</strong> 171 angstroms (0.0000000171 m) = Extreme Ultraviolet\n<strong>Primary ions seen:</strong>  8 times ionized iron (Fe IX)\n<strong>Characteristic temperature:</strong> 1 million K (1.8 million F)",
        # Magnetogram
        "Read more: <a href='https://svs.gsfc.nasa.gov/3989'>HMI Magnetogram</a>",
        # Colorized Magnetogram
        "<a href='https://sdo.gsfc.nasa.gov/assets/docs/HMI_M.ColorTable.pdf'>Read information on colorized magnetograms.</a>",
        # Intensitygram - colored
        "Read more: <a href='https://svs.gsfc.nasa.gov/3988'>HMI Intensity</a>",
        # Intensitygram - flattened
        "Read more: <a href='https://svs.gsfc.nasa.gov/3988'>HMI Intensity</a>",
        # Intensitygram
        "Read more: <a href='https://svs.gsfc.nasa.gov/3988'>HMI Intensity</a>",
        # Dopplergram
        "Read more: <a href='https://svs.gsfc.nasa.gov/3990'>HMI Dopplergram</a>"
    ]
    PHOTO_PATH = "assets/sun/"


# ISS
class ISS:
    API_BASE_URL = "http://api.open-notify.org/iss-now.json"


# User Info
NOMINATIM_REVERSE_API_BASE_URL = "https://nominatim.openstreetmap.org/reverse"


# Misc
TUTORIAL_TEXT = f"""
<code>astro* bot;</code> is designed with mobile devices in mind.

<code>astro* bot;</code> is an easy-to-use astronomical bot that provides you with all the necessary stargazing information including star maps (sky charts), weather and astronomical data, etc.

To get the most out of this bot, you are required to set a location (/setlocation). This location data is used for generating star maps, displaying weather and astronomical data at that specific location only. Users can delete their data at any time with the command /deletemyinfo.

As weather and astronomical data do not differ much within a few kilometers' range, feel free to turn off 'Precise Location' (on iOS) or choose "Approximate location" (on Android) for Telegram in Settings. When setting up your location, you can move the map around in the Telegram app to provide a location wherever you want too.

Press the menu button at the bottom left of your screen to view all the commands available.
"""