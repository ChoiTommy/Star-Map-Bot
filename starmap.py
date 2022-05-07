import json, time
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# star map URLs
STAR_MAP_URL = "https://www.heavens-above.com/SkyAndTelescope/StSkyChartPDF.ashx"
'''params: time, latitude, longitude, location, utcOffset'''
REST_OF_THE_URL = f"showEquator=false&showEcliptic=true&showStarNames=true&showPlanetNames=true&showConsNames=true&showConsLines=true&showConsBoundaries=false&showSpecials=false&use24hClock=true"
# 28800000ms == 28800s == 8 hours (UTC+8)


def send_star_map(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)

    if data.get(user_id) != None: # check_if_user_data_exists(update.effective_user):

        lat = str(data[user_id]["latitude"])
        longi = str(data[user_id]["longitude"])
        address = data[user_id]["address"].replace(',', "%2c").replace(' ', "%20")
        utcOffset = str(data[user_id]["utcOffset"])

        # time.time(): seconds (floating point) since the epoch in UTC
        fetch_target = f"{STAR_MAP_URL}?time={str(int(time.time()*1000))}&latitude={lat}&longitude={longi}&location={address}&utcOffset={utcOffset}&{REST_OF_THE_URL}"

        update.message.reply_document(document = fetch_target)
        update.message.reply_text("Enjoy the stunning stars\! Be considerate and *leave no trace* while stargazing\!", parse_mode=ParseMode.MARKDOWN_V2)
    else:
        update.message.reply_text("Please set your location with /setlocation first!")