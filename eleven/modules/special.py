import html
import json
import random
import PIL
import os
import urllib
import datetime
import time
import urbandict
import pyowm
from typing import Optional, List


from pyowm import timeutils, exceptions
from googletrans import Translator
import wikipedia
import base64
from bs4 import BeautifulSoup
from emoji import UNICODE_EMOJI

import requests
from telegram.error import BadRequest, Unauthorized, RetryAfter
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html, mention_markdown

from eleven import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, BAN_STICKER, API_WEATHER, spamcheck
from eleven.__main__ import STATS, USER_INFO
from eleven.modules.disable import DisableAbleCommandHandler
from eleven.modules.helper_funcs.extraction import extract_user
from eleven.modules.helper_funcs.filters import CustomFilters
from eleven.modules.sql import languages_sql as langsql
from eleven.modules.sql.users_sql import get_user_com_chats


from eleven.modules.languages import tl
from eleven.modules.helper_funcs.alternate import send_message


@run_async
def getlink(update, context):
    args = context.args
    if args:
        chat_id = int(args[0])
    else:
        send_message(update.effective_message, tl(update.effective_message, "You don't seem to be referring to chat"))
    chat = context.bot.getChat(chat_id)
    bot_member = chat.get_member(context.bot.id)
    if bot_member.can_invite_users:
        titlechat = context.bot.get_chat(chat_id).title
        invitelink = context.bot.get_chat(chat_id).invite_link
        send_message(update.effective_message, tl(update.effective_message, "Successfully retrieve the invite link in the group {}. \nInvite link : {}").format(titlechat, invitelink))
    else:
        send_message(update.effective_message, tl(update.effective_message, "I don't have access to the invitation link!"))
	
@run_async
def leavechat(update, context):
    args = context.args
    if args:
        chat_id = int(args[0])
    else:
        send_message(update.effective_message, tl(update.effective_message, "You don't seem to be referring to chat"))
    try:
        titlechat = context.bot.get_chat(chat_id).title
        context.bot.sendMessage(chat_id, tl(update.effective_message, "Goodbye everyone 😁"))
        context.bot.leaveChat(chat_id)
        send_message(update.effective_message, tl(update.effective_message, "I have left the group {}").format(titlechat))

    except BadRequest as excp:
        if excp.message == "Chat not found":
            send_message(update.effective_message, tl(update.effective_message, "Looks like I have been out or kicked in the group"))
        else:
            return

@run_async
@spamcheck
def ping(update, context):
    start_time = time.time()
    test = send_message(update.effective_message, "Pong!")
    end_time = time.time()
    ping_time = float(end_time - start_time)
    context.bot.editMessageText(chat_id=update.effective_chat.id, message_id=test.message_id,
                        text=tl(update.effective_message, "Pong!\nSpeed was: {0:.2f}s").format(round(ping_time, 2) % 60))
	   

@run_async
@spamcheck
def translate(update, context):
    msg = update.effective_message
    getlang = langsql.get_lang(update.effective_message.from_user.id)
    try:
        if msg.reply_to_message and msg.reply_to_message.text:
            args = update.effective_message.text.split()
            if len(args) >= 2:
                target = args[1]
                if "-" in target:
                    target2 = target.split("-")[1]
                    target = target.split("-")[0]
                else:
                    target2 = None
            else:
                if getlang:
                    target = getlang
                    target2 = None
                else:
                    raise IndexError
            teks = msg.reply_to_message.text
            exclude_list = UNICODE_EMOJI.keys()
            for emoji in exclude_list:
                if emoji in teks:
                    teks = teks.replace(emoji, '')
            message = update.effective_message
            trl = Translator()
            if target2 == None:
                deteksibahasa = trl.detect(teks)
                tekstr = trl.translate(teks, dest=target)
                send_message(update.effective_message, tl(update.effective_message, "Translated from `{}` to `{}`:\n`{}`").format(deteksibahasa.lang, target, tekstr.text), parse_mode=ParseMode.MARKDOWN)
            else:
                tekstr = trl.translate(teks, dest=target2, src=target)
                send_message(update.effective_message, tl(update.effective_message, "Translated from `{}` to `{}`:\n`{}`").format(target, target2, tekstr.text), parse_mode=ParseMode.MARKDOWN)

        else:
            args = update.effective_message.text.split(None, 2)
            if len(args) != 1:
                target = args[1]
                teks = args[2]
                target2 = None
                if "-" in target:
                    target2 = target.split("-")[1]
                    target = target.split("-")[0]
            else:
                target = getlang
                teks = args[1]
            exclude_list = UNICODE_EMOJI.keys()
            for emoji in exclude_list:
                if emoji in teks:
                    teks = teks.replace(emoji, '')
            trl = Translator()
            if target2 == None:
                deteksibahasa = trl.detect(teks)
                tekstr = trl.translate(teks, dest=target)
                return send_message(update.effective_message, tl(update.effective_message, "Translated from `{}` to `{}`:\n`{}`").format(deteksibahasa.lang, target, tekstr.text), parse_mode=ParseMode.MARKDOWN)
            else:
                tekstr = trl.translate(teks, dest=target2, src=target)
                send_message(update.effective_message, tl(update.effective_message, "Translated from `{}` to `{}`:\n`{}`").format(target, target2, tekstr.text), parse_mode=ParseMode.MARKDOWN)
    except IndexError:
        send_message(update.effective_message, tl(update.effective_message, "Reply to messages or write messages from other languages ​​to translate into the intended language\n\nExample: `/tr en-hi` to translate from English to Hindi\nOr use: `/tr id` for automatic detection and translating it into English"), parse_mode="markdown")
    except ValueError:
        send_message(update.effective_message, tl(update.effective_message, "The destination language is not found!"))
    else:
        return


@run_async
@spamcheck
def wiki(update, context):
    chat_id = update.effective_chat.id
    args = update.effective_message.text.split(None, 1)
    teks = args[1]
    getlang = langsql.get_lang(chat_id)
    if str(getlang) == "pt":
        wikipedia.set_lang("pt")
    else:
        wikipedia.set_lang("en")
    try:
        pagewiki = wikipedia.page(teks)
    except wikipedia.exceptions.PageError:
        send_message(update.effective_message, tl(update.effective_message, "Results not found"))
        return
    except wikipedia.exceptions.DisambiguationError as refer:
        rujuk = str(refer).split("\n")
        if len(rujuk) >= 6:
            batas = 6
        else:
            batas = len(rujuk)
        teks = ""
        for x in range(batas):
            if x == 0:
                if getlang == "pt":
                    teks += rujuk[x].replace('may refer to', 'can refer to')+"\n"
                else:
                    teks += rujuk[x]+"\n"
            else:
                teks += "- `"+rujuk[x]+"`\n"
        send_message(update.effective_message, teks, parse_mode="markdown")
        return
    except IndexError:
        send_message(update.effective_message, tl(update.effective_message, "Write a message to search from the wikipedia source"))
        return
    judul = pagewiki.title
    summary = pagewiki.summary
    if update.effective_message.chat.type == "private":
        send_message(update.effective_message, tl(update.effective_message, "Results of {} is:\n\n<b>{}</b>\n{}").format(teks, judul, summary), parse_mode=ParseMode.HTML)
    else:
        if len(summary) >= 200:
            judul = pagewiki.title
            summary = summary[:200]+"..."
            button = InlineKeyboardMarkup([[InlineKeyboardButton(text=tl(update.effective_message, "Read More..."), url="t.me/{}?start=wiki-{}".format(context.bot.username, teks.replace(' ', '_')))]])
        else:
            button = None
        send_message(update.effective_message, tl(update.effective_message, "Results of {} is:\n\n<b>{}</b>\n{}").format(teks, judul, summary), parse_mode=ParseMode.HTML, reply_markup=button)

	
@run_async
@spamcheck
def urbandictionary(update, context):
    args = context.args
    if args:
        text = " ".join(args)
        try:
            mean = urbandict.define(text)
        except Exception as err:
            send_message(update.effective_message, "Error: " + str(err))
            return
        if len(mean) >= 0:
            teks = ""
            if len(mean) >= 3:
                for x in range(3):
                    teks = "*Result of {}*\n\n*{}*\n*Meaning:*\n`{}`\n\n*Example:*\n`{}`\n\n".format(text, mean[x].get("word")[:-7], mean[x].get("def"), mean[x].get("example"))
            else:
                for x in range(len(mean)):
                    teks = "*Result of {}*\n\n*{}*\n**Meaning:*\n`{}`\n\n*Example:*\n`{}`\n\n".format(text, mean[x].get("word")[:-7], mean[x].get("def"), mean[x].get("example"))
            send_message(update.effective_message, teks, parse_mode=ParseMode.MARKDOWN)
        else:
            send_message(update.effective_message, "{} couldn't be found in urban dictionary!".format(text), parse_mode=ParseMode.MARKDOWN)
    else:
        send_message(update.effective_message, "Use `/ud <text` for search meaning from urban dictionary.", parse_mode=ParseMode.MARKDOWN)

@run_async
def log(update, context):
    message = update.effective_message
    eventdict = message.to_dict()
    jsondump = json.dumps(eventdict, indent=4)
    send_message(update.effective_message, jsondump)

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

@run_async
def get_user_common_chats(update, context):
    args = context.args	
    msg = update.effective_message
    user = extract_user(msg, args)
    if not user:
        msg.reply_text("I share no common chats with the void.")
        return
    common_list = get_user_com_chats(user)
    if not common_list:
        msg.reply_text("No common chats with this user!")
        return
    name = bot.get_chat(user).first_name
    text = f"<b>Common chats with {name}</b>\n"
    for chat in common_list:
        try:
            chat_name = bot.get_chat(chat).title
            sleep(0.3)
            text += f"• <code>{chat_name}</code>\n"
        except BadRequest:
            pass
        except Unauthorized:
            pass
        except RetryAfter as e:
            sleep(e.retry_after)
            
    if len(text) < 4096:
        msg.reply_text(text, parse_mode="HTML")
    else:
        with open("common_chats.txt", 'w') as f:
            f.write(text)
        with open("common_chats.txt", 'rb') as f:
            msg.reply_document(f)
        os.remove("common_chats.txt")

__help__ = "exclusive_help"

__mod_name__ = "🔥ELEVEN Special🔥"

PING_HANDLER = DisableAbleCommandHandler("ping", ping, filters=Filters.user(OWNER_ID))
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True, filters=Filters.user(OWNER_ID))
LEAVECHAT_HANDLER = CommandHandler(["leavechat", "leavegroup", "leave"], leavechat, pass_args=True, filters=Filters.user(OWNER_ID))
TRANSLATE_HANDLER = DisableAbleCommandHandler(["tr", "tl"], translate)
WIKIPEDIA_HANDLER = DisableAbleCommandHandler("wiki", wiki)
UD_HANDLER = DisableAbleCommandHandler("ud", urbandictionary, pass_args=True)
LOG_HANDLER = DisableAbleCommandHandler("log", log, filters=Filters.user(OWNER_ID))
COMMON_CHATS_HANDLER = CommandHandler("getchats", get_user_common_chats, pass_args=True, filters=Filters.user(OWNER_ID))

dispatcher.add_handler(PING_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(LEAVECHAT_HANDLER)
dispatcher.add_handler(TRANSLATE_HANDLER)
dispatcher.add_handler(WIKIPEDIA_HANDLER)
dispatcher.add_handler(UD_HANDLER)
dispatcher.add_handler(LOG_HANDLER)
dispatcher.add_handler(COMMON_CHATS_HANDLER)
