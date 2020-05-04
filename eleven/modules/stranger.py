import html
import json
import random
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Optional, List
import time
import locale

import requests
from telegram.error import BadRequest, Unauthorized
from telegram import Message, Chat, Update, Bot, MessageEntity, InlineKeyboardMarkup
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html, mention_markdown

import eleven.modules.stranger_strings as stranger_strings
from eleven import dispatcher, OWNER_ID, spamcheck
from eleven.modules.disable import DisableAbleCommandHandler
from eleven.modules.helper_funcs.extraction import extract_user
from eleven.modules.helper_funcs.filters import CustomFilters
from eleven.modules.helper_funcs.msg_types import get_message_type
from eleven.modules.helper_funcs.misc import build_keyboard_alternate
from eleven.modules.helper_funcs.chat_status import user_admin

from eleven.modules.languages import tl
from eleven.modules.sql import languages_sql as lang_sql
import eleven.modules.sql.feds_sql as feds_sql
from eleven.modules.helper_funcs.alternate import send_message

# Change language locale to Indonesia
# Install language:
# - sudo apt-get install language-pack-id language-pack-id-base manpages
# locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')

normiefont = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
weebyfont = ['卂','乃','匚','刀','乇','下','厶','卄','工','丁','长','乚','从','𠘨','口','尸','㔿','尺','丂','丅','凵','リ','山','乂','丫','乙']

#sleep how many times after each edit in 'police' 
EDIT_SLEEP = 1
#edit how many times in 'police' 
EDIT_TIMES = 3

police_siren = [
            "🔴🔴🔴⬜️⬜️⬜️🔵🔵🔵\n🔴🔴🔴⬜️⬜️⬜️🔵🔵🔵\n🔴🔴🔴⬜️⬜️⬜️🔵🔵🔵",
            "🔵🔵🔵⬜️⬜️⬜️🔴🔴🔴\n🔵🔵🔵⬜️⬜️⬜️🔴🔴🔴\n🔵🔵🔵⬜️⬜️⬜️🔴🔴🔴"
]

@run_async
@spamcheck
def runs(update, context):
    send_message(update.effective_message, random.choice(tl(update.effective_message(stranger_string.RUN_STRINGS))))


@run_async
@spamcheck
def slap(update, context):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)

    user_id = extract_user(update.effective_message, args)
    if user_id == context.bot.id or user_id == 777000:
        user1 = "[{}](tg://user?id={})".format(context.bot.first_name, context.bot.id)
        user2 = curr_user
    elif user_id:
        slapped_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if slapped_user.username:
            user2 = "@" + escape_markdown(slapped_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(slapped_user.first_name,
                                                   slapped_user.id)

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(context.bot.first_name, context.bot.id)
        user2 = curr_user

    temp = random.choice(stranger_strings.SLAP_TEMPLATES)
    item = random.choice(stranger_strings.ITEMS)
    hit = random.choice(stranger_strings.HIT)
    throw = random.choice(stranger_strings.THROW)
    emoji = random.choice(stranger_strings.EMOJI)

    repl = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw, emoji=emoji)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)


@run_async
@spamcheck
def weebify(update, context):
    args = context.args
    msg = update.effective_message
    if args:
        string = " ".join(args).lower()
    elif msg.reply_to_message:
        string = msg.reply_to_message.text.lower()
    else:
        msg.reply_text("Enter some text to weebify or reply to someone's message!")
        return
        
    for normiecharacter in string:
        if normiecharacter in normiefont:
            weebycharacter = weebyfont[normiefont.index(normiecharacter)]
            string = string.replace(normiecharacter, weebycharacter)
 
    if msg.reply_to_message:
        msg.reply_to_message.reply_text(string)
    else:
        msg.reply_text(string)


@run_async
@spamcheck
def pat(update, context):
    args = context.args
    chat_id = update.effective_chat.id
    msg = str(update.message.text)
    try:
        msg = msg.split(" ", 1)[1]
    except IndexError:
        msg = ""
    msg_id = update.effective_message.reply_to_message.message_id if update.effective_message.reply_to_message else update.effective_message.message_id
    pats = []
    pats = json.loads(urllib.request.urlopen(urllib.request.Request(
    'http://headp.at/js/pats.json',
    headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) '
         'Gecko/20071127 Firefox/2.0.0.11'}
    )).read().decode('utf-8'))
    if "@" in msg and len(msg) > 5:
        context.bot.send_photo(chat_id, f'https://headp.at/pats/{urllib.parse.quote(random.choice(pats))}', caption=msg)
    else:
        context.bot.send_photo(chat_id, f'https://headp.at/pats/{urllib.parse.quote(random.choice(pats))}', reply_to_message_id=msg_id)
    #if msg.from_user.username:
    #    curr_user = "@" + escape_markdown(msg.from_user.username)
    #else:
    curr_user = "{}".format(mention_markdown(msg.from_user.id, msg.from_user.first_name))

    user_id = extract_user(update.effective_message, args)
    if user_id and user_id != "error":
        slapped_user = context.bot.get_chat(user_id)
        user1 = curr_user
        #if slapped_user.username:
        #    user2 = "@" + escape_markdown(slapped_user.username)
        #else:
        user2 = "{}".format(mention_markdown(slapped_user.id, slapped_user.first_name))

    # if no target found, bot targets the sender
    else:
        user1 = "{}".format(mention_markdown(context.bot.id, context.bot.first_name))
        user2 = curr_user

    temp = random.choice(tl(update.effective_message(stranger_strings.SLAP_TEMPLATES)))
    item = random.choice(tl(update.effective_message(stranger_strings.ITEMS)))
    hit = random.choice(tl(update.effective_message(stranger_strings.HIT)))
    throw = random.choice(tl(update.effective_message(stranger_strings.THROW)))

    repl = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    send_message(update.effective_message, repl, parse_mode=ParseMode.MARKDOWN)
    
@run_async
def decide(update, context):
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(stranger_strings.DECIDE))
    
@run_async
def toss(bot: Bot, update: Update):
    update.message.reply_text(random.choice(stranger_strings.TOSS))
    
@user_admin
@run_async
def police(update, context):
    msg = update.effective_message.reply_text('Police is coming!')
    for x in range(EDIT_TIMES):
        msg.edit_text(police_siren[x%2]) 
        time.sleep(EDIT_SLEEP)
    msg.edit_text('Police is here!')    

@run_async
@spamcheck
def fortune(update, context):
    text = ""
    if random.randint(1, 10) >= 7:
        text += random.choice(tl(update.effective_message, "RAMALAN_FIRST"))
    text += random.choice(tl(update.effective_message, "RAMALAN_STRINGS"))
    send_message(update.effective_message, text)   

# /ip is for private use
__help__ = "stranger_help"

__mod_name__ = "Stranger Things"


WEEBIFY_HANDLER = DisableAbleCommandHandler("weebify", weebify, pass_args=True)
PAT_HANDLER = DisableAbleCommandHandler("pat", pat)

RUNS_HANDLER = DisableAbleCommandHandler(["runs", "lari"], runs)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, pass_args=True)
DECIDE_HANDLER = DisableAbleCommandHandler("decide", decide)
TOSS_HANDLER = DisableAbleCommandHandler("toss", toss)
POLICE_HANDLER = DisableAbleCommandHandler("police", police)
FORTUNE_HANDLER = DisableAbleCommandHandler("fortune", fortune)

dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(WEEBIFY_HANDLER)
dispatcher.add_handler(PAT_HANDLER)
dispatcher.add_handler(DECIDE_HANDLER)
dispatcher.add_handler(TOSS_HANDLER)
dispatcher.add_handler(POLICE_HANDLER) 
dispatcher.add_handler(FORTUNE_HANDLER)
