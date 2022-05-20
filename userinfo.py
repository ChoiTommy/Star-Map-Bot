"""
userinfo is a module that consists of functions regarding user's info.

Usage:
Command /myinfo is defined by show_user_info
Command /deletemyinfo is defined by deletion_confirmation and delete_user_info
Command /cancel is defined by cancel_deletion. It serves the same function as settings.cancel.
"""

import helpers
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import CallbackContext, ConversationHandler


def show_user_info(update: Update, context: CallbackContext) -> None:
    """Display user info when the command /myinfo is called. User info consists of latitude, longitude, address and timezone."""

    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)

    if user_id in data:
        update.message.reply_text(
            text = (f'Hi @{update.effective_user.username}, \n'
                    'Your currently set location is \n'
                    f'Latitude: {data[user_id]["latitude"]} \n'
                    f'Longitude: {data[user_id]["longitude"]} \n'
                    f'Location: <i>{data[user_id]["address"]}</i> \n'
                    f'Timezone: {helpers.utcOffset_to_tzstring(data[user_id]["utcOffset"])} \n\n'

                    '/setlocation to modify. /deletemyinfo to delete your data. \n'
            ),
            parse_mode = ParseMode.HTML
        )
    else:
        update.message.reply_text(
            text = (f'Hi @{update.effective_user.username}, \n'
                    'You have yet to set any location. \n'
                    '/setlocation to start off. \n'
            )
        )


def deletion_confirmation(update: Update, context: CallbackContext) -> int:
    """Ask for confirmation to delete the user info from the server. Return Conversation.END if user has no data on the server, else returns 0."""

    user_id = str(update.effective_user.id)
    with open("locations.json", 'r') as file:
        data = json.load(file)
    context.user_data["JSON"] = data

    if user_id not in data:
        update.message.reply_text(
            text = "Hi new user, rest assured we have not collected any data from you, so nothing has been erased. " \
                    "Perhaps you can try /setlocation and give me something to delete afterwards?"
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            "Are you sure you want to delete your location data? Note that this action cannot be undone.",
            reply_markup = ReplyKeyboardMarkup([['Yes', 'No']], resize_keyboard = True)
        )
        return 0


def delete_user_info(update: Update, context: CallbackContext) -> int:
    """Perform deletion on users' data if 'Yes' is retrieved. Return ConversationHandler.END to halt the ConversationHandler."""

    if update.message.text == 'Yes':
        user_id = str(update.effective_user.id)
        del context.user_data["JSON"][user_id]
        with open("locations.json", 'w') as file:
            json.dump(context.user_data["JSON"], file, indent = 4)
        update.message.reply_text(
            text = ("Voilà! I have erased your existence. Keep it up and leave no trace in the cyber world! \n"
                    "/myinfo <- click it to see for yourself, scumbag"
            ),
            reply_markup = ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        return cancel_deletion(update, context)


def cancel_deletion(update: Update, context: CallbackContext) -> int:
    """Cancel the deletion operation with the command /cancel. Return ConversationHandler.END"""

    update.message.reply_text("Got it! My generous user. Your data are still in my hands.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END