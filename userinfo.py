import json
from telegram import Update
from telegram.ext import CallbackContext

def utcOffset_to_tzstring(offset) -> str:
    offset /= 3600000 # 3600000 ms
    tz_hour = int(offset)
    tz_minutes = int((abs(offset) - abs(tz_hour)) * 60)
    if tz_hour >= 0:
        return f"UTC+{tz_hour}:{tz_minutes if tz_minutes>=10 else '0'+str(tz_minutes)}"
    else:
        return f"UTC{tz_hour}:{tz_minutes if tz_minutes>=10 else '0'+str(tz_minutes)}"

def show_user_info(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)

    if data.get(str(update.effective_user.id)) != None: # check_if_user_data_exists(update.effective_user):
        update.message.reply_text(
            f'''Hi @{update.effective_user.username},
Your currently set location is
Latitude: {data[user_id]["latitude"]}
Longitude: {data[user_id]["longitude"]}
Location: {data[user_id]["address"]}
Timezone: {utcOffset_to_tzstring(data[user_id]["utcOffset"])}

/setlocation to modify. /deletemyinfo to delete your data.
            '''
        )
    else:
        update.message.reply_text(
            f'''Hi @{update.effective_user.username},
You have yet to set any location.
/setlocation to start off.
            '''
        )

def delete_user_info(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)
    if data.get(user_id) == None:
        update.message.reply_text("Hi new user, rest assured we have not collected any data from you, so nothing has been erased. Perhaps you can try /setlocation and give me something to delete afterwards?")
    else:
        del data[user_id]
        with open("locations.json", 'w') as file:
            json.dump(data, file, indent = 4)
        update.message.reply_text("Voilà! I have erased your existence (on my server). Keep it up and leave no trace in the cyber world! \n/myinfo <- click it to see for yourself, scumbag")