import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

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

    if user_id in data:
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

def deletion_confirmation(update: Update, context: CallbackContext) -> int:
    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)
    context.user_data["JSON"] = data

    if user_id not in data:
        update.message.reply_text("Hi new user, rest assured we have not collected any data from you, so nothing has been erased. Perhaps you can try /setlocation and give me something to delete afterwards?")
        return ConversationHandler.END
    else:
        update.message.reply_text(
            "Are you sure you want to delete your location data? Note that this action cannot be undone.",
            reply_markup = ReplyKeyboardMarkup([['Yes', 'No']], resize_keyboard = True)
        )
        return 0

def delete_user_info(update: Update, context: CallbackContext) -> int:
    if update.message.text == 'Yes':
        user_id = str(update.effective_user.id)
        del context.user_data["JSON"][user_id]
        with open("locations.json", 'w') as file:
            json.dump(context.user_data["JSON"], file, indent = 4)
        update.message.reply_text("Voilà! I have erased your existence (on my server). Keep it up and leave no trace in the cyber world! \n/myinfo <- click it to see for yourself, scumbag", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        return cancel_deletion(update, context)

def cancel_deletion(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Got it! My generous user. Your data are still in my hands.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END