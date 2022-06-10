"""
sun is a module that consists of functions fetching and displaying near-real-time sun photos from NASA.

Usage:
Command /sun is defined by send_sun_photo

TODO separate out sun data to a new file
"""

import helpers
import time, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, error
from telegram.ext import CallbackContext
from telegram.constants import ParseMode


SUN_PHOTO_URLS = [  # 19 photos, indices from 0..18
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

SUN_PHOTO_NAMES = [
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

SUN_PHOTO_DESCRIPTIONS = [
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


async def fetch_sun_photos(context: CallbackContext) -> None: # Possibility to switch to asynchronous?
    """Fetch all the sun photos from the server. This is run every 15 mins."""

    for i in range(len(SUN_PHOTO_URLS)):
        img_data = requests.get(SUN_PHOTO_URLS[i], stream=True).content
        with open(f"assets/sun/{i}.jpg", "wb") as f:
            f.write(img_data)

    with open("assets/sun/log.txt", "w") as txt:
        txt.write(f"{helpers.get_current_date_time_string(0)} UTC")   # UTC time


async def send_sun_photo(update: Update, context: CallbackContext) -> None:
    """Send a photo of the current sun."""

    with open("assets/sun/log.txt", 'r') as txt:
        last_fetched = txt.read()
    default_starting_point = 0

    await update.message.reply_photo(
        photo = open(f"assets/sun/{default_starting_point}.jpg", "rb"),
        caption = (f"🌞 Live Photos of the Sun \n"
                    f"{SUN_PHOTO_NAMES[default_starting_point]} \n"
                    f"({last_fetched})"),
        reply_markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton("<<", callback_data=f"SUN_{(default_starting_point - 1) % 19}"), InlineKeyboardButton("↻", callback_data=f"SUN_{default_starting_point}"), InlineKeyboardButton(">>", callback_data=f"SUN_{(default_starting_point + 1) % 19}")],
                            [InlineKeyboardButton("⇣ Show description", callback_data=f"SHOW_{default_starting_point}")]
                        ])
    )


async def show_description(update: Update, context: CallbackContext) -> str:
    """Expand the message to show the description.

    Returns:
        str: status
    """

    sun_number = int(update.callback_query.data[5:])

    await update.callback_query.message.edit_caption(
        caption = (f"{update.callback_query.message.caption} \n"
                    "************************************ \n"
                    f"{SUN_PHOTO_DESCRIPTIONS[sun_number]}"),
        parse_mode = ParseMode.HTML,
        reply_markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton("<<", callback_data=f"SUN_{(sun_number - 1) % 19}"), InlineKeyboardButton("↻", callback_data=f"SUN_{sun_number}"), InlineKeyboardButton(">>", callback_data=f"SUN_{(sun_number + 1) % 19}")],
                            [InlineKeyboardButton("⇡ Hide description", callback_data=f"HIDE_{sun_number}")]
                        ])
    )
    return "Description shown"


async def hide_description(update: Update, context: CallbackContext) -> str:
    """Collapse the message and remove the description part.

    Returns:
        str: status
    """

    sun_number = int(update.callback_query.data[5:])

    await update.callback_query.message.edit_caption(
        caption = (f"{update.callback_query.message.caption[:update.callback_query.message.caption.find('*')]}"),
        reply_markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton("<<", callback_data=f"SUN_{(sun_number - 1) % 19}"), InlineKeyboardButton("↻", callback_data=f"SUN_{sun_number}"), InlineKeyboardButton(">>", callback_data=f"SUN_{(sun_number + 1) % 19}")],
                            [InlineKeyboardButton("⇣ Show description", callback_data=f"SHOW_{sun_number}")]
                        ])
    )
    return "Description hidden"


async def update_sun_photo(update: Update, context: CallbackContext) -> str:
    """Cycle through the sun photo list or refresh the current one.

    Returns:
        str: status
    """

    sun_number = int(update.callback_query.data[4:])
    with open("assets/sun/log.txt", 'r') as txt:
        last_fetched = txt.read()

    try:
        await update.callback_query.message.edit_media(
            media = InputMediaPhoto(
                media = open(f"assets/sun/{sun_number}.jpg", "rb"),
                caption = (f"🌞 Live Photos of the Sun \n"
                            f"{SUN_PHOTO_NAMES[sun_number]} \n"
                            f"({last_fetched})")
            ),
            reply_markup = InlineKeyboardMarkup([
                                [InlineKeyboardButton("<<", callback_data=f"SUN_{(sun_number - 1) % 19}"), InlineKeyboardButton("↻", callback_data=f"SUN_{sun_number}"), InlineKeyboardButton(">>", callback_data=f"SUN_{(sun_number + 1) % 19}")],
                                [InlineKeyboardButton("⇣ Show description", callback_data=f"SHOW_{sun_number}")]
                            ])
        )
    except error.BadRequest:
        return "The photo is up-to-date. Please try again later."
    else:
        return "Sun photo refreshed"
