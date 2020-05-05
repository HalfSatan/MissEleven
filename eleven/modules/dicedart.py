# This Is A Simple requests Module for sendDice Method
# its Coded By @TheDarkW3b

import requests
import logging

#Telegram Neccessary Things 
from telegram import Message, Chat, Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import run_async

#eleven
from eleven import dispatcher, updater, TOKEN, spamcheck
from eleven.modules.disable import DisableAbleCommandHandler
from eleven.modules.helper_funcs.chat_status import user_admin

@run_async
@user_admin
@spamcheck
def dice(update, context):
    chat = update.effective_chat
    url = f"https://api.telegram.org/bot{TOKEN}/sendDice?chat_id={chat.id}"
    requests.get(url)

@run_async
@user_admin
@spamcheck
def darts(update, context):
    chat = update.effective_chat
    url = f"https://api.telegram.org/bot{TOKEN}/sendDice?chat_id={chat.id}&emoji=🎯"
    requests.get(url)


DICE_HANDLER = DisableAbleCommandHandler("dice", dice)
DARTS_HANDLER = DisableAbleCommandHandler("darts", darts)

dispatcher.add_handler(DICE_HANDLER)
dispatcher.add_handler(DARTS_HANDLER)
