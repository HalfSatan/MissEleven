import html
import json
import random
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Optional, List
import time
import locale
import re

import requests
from telegram.error import BadRequest, Unauthorized
from telegram import Message, Chat, Update, Bot, MessageEntity, InlineKeyboardMarkup
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html, mention_markdown

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


normiefont = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
weebyfont = ['卂','乃','匚','刀','乇','下','厶','卄','工','丁','长','乚','从','𠘨','口','尸','㔿','尺','丂','丅','凵','リ','山','乂','丫','乙']

TOSS = (
    "Heads",
    "Tails",
)

DECIDE = (
    "Yes.",
    "No.",
    "Maybe.",
)

#sleep how many times after each edit in 'police' 
EDIT_SLEEP = 1
#edit how many times in 'police' 
EDIT_TIMES = 3

police_siren = [
            "🔴🔴🔴⬜️⬜️⬜️🔵🔵🔵\n🔴🔴🔴⬜️⬜️⬜️🔵🔵🔵\n🔴🔴🔴⬜️⬜️⬜️🔵🔵🔵",
            "🔵🔵🔵⬜️⬜️⬜️🔴🔴🔴\n🔵🔵🔵⬜️⬜️⬜️🔴🔴🔴\n🔵🔵🔵⬜️⬜️⬜️🔴🔴🔴"
]

WIDE_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
WIDE_MAP[0x20] = 0x3000

@run_async
@spamcheck
def runs(update, context):
    send_message(update.effective_message, random.choice(tl(update.effective_message, "RUN_STRINGS")))
    
@run_async
@spamcheck
def insults(update, context):
    message = update.effective_message
    text = random.choice(tl(update.effective_message, "INSULT_STRINGS"))

    if message.reply_to_message:
        message.reply_to_message.reply_text(text)
    else:
        message.reply_text(text)

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

    temp = random.choice(tl(update.effective_message, "SLAP_TEMPLATES"))
    item = random.choice(tl(update.effective_message, "ITEMS"))
    hit = random.choice(tl(update.effective_message, "HIT"))
    throw = random.choice(tl(update.effective_message, "THROW"))
    emoji = random.choice(tl(update.effective_message, "EMOJI"))

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
def decide(update, context):
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(DECIDE))
    

@run_async
def toss(update, context):
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(TOSS))
    
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

    
@spamcheck
@run_async
def stretch(update, context):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to meme.")
    else:
        count = random.randint(3, 10)
        reply_text = re.sub(
            r'([aeiouAEIOUａｅｉｏｕＡＥＩＯＵ])',
            (r'\1' * count),
            message.reply_to_message.text)
        message.reply_to_message.reply_text(reply_text)



@spamcheck
@run_async
def vapor(update, context):
    args = context.args
    message = update.effective_message
    chat = update.effective_chat

    noreply = False
    if message.reply_to_message:
        data = message.reply_to_message.text
    elif args:
        noreply = True
        data = message.text.split(None, 1)[1]
    else:
        noreply = True
        data = tl(chat.id, "I need a message to meme.")

    reply_text = str(data).translate(WIDE_MAP)

    if noreply:
        message.reply_text(reply_text)
    else:
        message.reply_to_message.reply_text(reply_text)


# D A N K modules by @deletescape ^^^
# Less D A N K modules by @skittles9823 # holi fugg I did some maymays vvv


# based on
# https://github.com/wrxck/mattata/blob/master/plugins/copypasta.mattata
@spamcheck
@run_async
def copypasta(update, context):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to meme.")
    else:
        emojis = [
            "😂",
            "😂",
            "👌",
            "✌",
            "💞",
            "👍",
            "👌",
            "💯",
            "🎶",
            "👀",
            "😂",
            "👓",
            "👏",
            "👐",
            "🍕",
            "💥",
            "🍴",
            "💦",
            "💦",
            "🍑",
            "🍆",
            "😩",
            "😏",
            "👉👌",
            "👀",
            "👅",
            "😩",
            "🚰"]
        reply_text = random.choice(emojis)
        # choose a random character in the message to be substituted with 🅱️
        b_char = random.choice(message.reply_to_message.text).lower()
        for c in message.reply_to_message.text:
            if c == " ":
                reply_text += random.choice(emojis)
            elif c in emojis:
                reply_text += c
                reply_text += random.choice(emojis)
            elif c.lower() == b_char:
                reply_text += "🅱️"
            else:
                if bool(random.getrandbits(1)):
                    reply_text += c.upper()
                else:
                    reply_text += c.lower()
        reply_text += random.choice(emojis)
        message.reply_to_message.reply_text(reply_text)


@spamcheck
@run_async
def bmoji(update, context):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to meme.")
    else:
        # choose a random character in the message to be substituted with 🅱️
        b_char = random.choice(message.reply_to_message.text).lower()
        reply_text = message.reply_to_message.text.replace(
            b_char, "🅱️").replace(b_char.upper(), "🅱️")
        message.reply_to_message.reply_text(reply_text)  
        
# shitty maymay modules made by @divadsn ^^^
@spamcheck
@run_async
def shout(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args

    noreply = False
    if message.reply_to_message:
        data = message.reply_to_message.text
    elif args:
        noreply = True
        data = " ".join(args)
    else:
        noreply = True
        data = tl(chat.id, "I need a message to meme.")

    msg = "```"
    result = []
    result.append(' '.join([s for s in data]))
    for pos, symbol in enumerate(data[1:]):
        result.append(symbol + ' ' + '  ' * pos + symbol)
    result = list("\n".join(result))
    result[0] = data[0]
    result = "".join(result)
    msg = "```\n" + result + "```"
    return update.effective_message.reply_text(msg, parse_mode="MARKDOWN")

@spamcheck
@run_async
def clapmoji(update, context):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to meme.")
    else:
        reply_text = "👏 "
        reply_text += message.reply_to_message.text.replace(" ", " 👏 ")
        reply_text += " 👏"
        message.reply_to_message.reply_text(reply_text)

        
__help__ = "stranger_help"

__mod_name__ = "Stranger Things 👹"


WEEBIFY_HANDLER = DisableAbleCommandHandler("weebify", weebify, pass_args=True)

RUNS_HANDLER = DisableAbleCommandHandler(["runs", "lari"], runs)
INSULTS_HANDLER = DisableAbleCommandHandler(["insults", "abuse"], insults)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, pass_args=True)
DECIDE_HANDLER = DisableAbleCommandHandler("decide", decide)
TOSS_HANDLER = DisableAbleCommandHandler("toss", toss)
POLICE_HANDLER = DisableAbleCommandHandler("police", police)
FORTUNE_HANDLER = DisableAbleCommandHandler("fortune", fortune)
STRETCH_HANDLER = DisableAbleCommandHandler("stretch", stretch, pass_args=True)
VAPOR_HANDLER = DisableAbleCommandHandler("vapor", vapor, pass_args=True)
COPYPASTA_HANDLER = DisableAbleCommandHandler("cp", copypasta, pass_args=True)
CLAPMOJI_HANDLER = DisableAbleCommandHandler("clap", clapmoji, pass_args=True)
BMOJI_HANDLER = DisableAbleCommandHandler("bify", bmoji, pass_args=True)
SHOUT_HANDLER = DisableAbleCommandHandler("shout", shout, pass_args=True)

dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(INSULTS_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(WEEBIFY_HANDLER)
dispatcher.add_handler(DECIDE_HANDLER)
dispatcher.add_handler(TOSS_HANDLER)
dispatcher.add_handler(POLICE_HANDLER) 
dispatcher.add_handler(FORTUNE_HANDLER)
dispatcher.add_handler(STRETCH_HANDLER)
dispatcher.add_handler(VAPOR_HANDLER)
dispatcher.add_handler(COPYPASTA_HANDLER)
dispatcher.add_handler(CLAPMOJI_HANDLER)
dispatcher.add_handler(BMOJI_HANDLER)
dispatcher.add_handler(SHOUT_HANDLER)
