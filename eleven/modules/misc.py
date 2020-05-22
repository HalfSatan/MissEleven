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

from eleven import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, BAN_STICKER, spamcheck
from eleven.__main__ import STATS, USER_INFO
from eleven.modules.disable import DisableAbleCommandHandler
from eleven.modules.helper_funcs.extraction import extract_user
from eleven.modules.helper_funcs.filters import CustomFilters
from eleven.modules.helper_funcs.msg_types import get_message_type
from eleven.modules.helper_funcs.misc import build_keyboard_alternate

from eleven.modules.languages import tl
from eleven.modules.sql import languages_sql as lang_sql
import eleven.modules.sql.feds_sql as feds_sql
from eleven.modules.helper_funcs.alternate import send_message


BASE_URL = 'https://del.dog'


@run_async
@spamcheck
def paste(update, context):
    args = context.args
    message = update.effective_message

    if message.reply_to_message:
        data = message.reply_to_message.text
    elif len(args) >= 1:
        data = message.text.split(None, 1)[1]
    else:
        message.reply_text("What am I supposed to do with this?!")
        return

    r = requests.post(f'{BASE_URL}/documents', data=data.encode('utf-8'))

    if r.status_code == 404:
        update.effective_message.reply_text('Failed to reach dogbin')
        r.raise_for_status()

    res = r.json()

    if r.status_code != 200:
        update.effective_message.reply_text(res['message'])
        r.raise_for_status()

    key = res['key']
    if res['isUrl']:
        reply = f'Shortened URL: {BASE_URL}/{key}\nYou can view stats, etc. [here]({BASE_URL}/v/{key})'
    else:
        reply = f'{BASE_URL}/{key}'
    update.effective_message.reply_text(reply, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


@run_async
@spamcheck
def get_paste_content(update, context):
    args = context.args
    message = update.effective_message

    if len(args) >= 1:
        key = args[0]
    else:
        message.reply_text("Please supply a paste key!")
        return

    format_normal = f'{BASE_URL}/'
    format_view = f'{BASE_URL}/v/'

    if key.startswith(format_view):
        key = key[len(format_view):]
    elif key.startswith(format_normal):
        key = key[len(format_normal):]

    r = requests.get(f'{BASE_URL}/raw/{key}')

    if r.status_code != 200:
        try:
            res = r.json()
            update.effective_message.reply_text(res['message'])
        except Exception:
            if r.status_code == 404:
                update.effective_message.reply_text('Failed to reach dogbin')
            else:
                update.effective_message.reply_text('Unknown error occured')
        r.raise_for_status()

    update.effective_message.reply_text('```' + escape_markdown(r.text) + '```', parse_mode=ParseMode.MARKDOWN)


@run_async
@spamcheck
def get_paste_stats(update, context):
    args = context.args
    message = update.effective_message

    if len(args) >= 1:
        key = args[0]
    else:
        message.reply_text("Please supply a paste key!")
        return

    format_normal = f'{BASE_URL}/'
    format_view = f'{BASE_URL}/v/'

    if key.startswith(format_view):
        key = key[len(format_view):]
    elif key.startswith(format_normal):
        key = key[len(format_normal):]

    r = requests.get(f'{BASE_URL}/documents/{key}')

    if r.status_code != 200:
        try:
            res = r.json()
            update.effective_message.reply_text(res['message'])
        except Exception:
            if r.status_code == 404:
                update.effective_message.reply_text('Failed to reach dogbin')
            else:
                update.effective_message.reply_text('Unknown error occured')
        r.raise_for_status()

    document = r.json()['document']
    key = document['_id']
    views = document['viewCount']
    reply = f'Stats for **[/{key}]({BASE_URL}/{key})**:\nViews: `{views}`'
    update.effective_message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
	
@run_async
def get_bot_ip(update, context):
    """ Sends the bot's IP address, so as to be able to ssh in if necessary.
        OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    send_message(update.effective_message, res.text)


@run_async
@spamcheck
def get_id(update, context):
    args = context.args
    user_id = extract_user(update.effective_message, args)
    if user_id and user_id != "error":
        if update.effective_message.reply_to_message and update.effective_message.reply_to_message.forward_from:
            user1 = update.effective_message.reply_to_message.from_user
            user2 = update.effective_message.reply_to_message.forward_from
            text = tl(update.effective_message, "The original sender, {}, has an ID of `{}`.\nThe forwarder, {}, has an ID of `{}`.").format(
                    escape_markdown(user2.first_name),
                    user2.id,
                    escape_markdown(user1.first_name),
                    user1.id)
            if update.effective_message.chat.type != "private":
                text += "\n" + tl(update.effective_message, "This group's id is `{}`.").format(update.effective_message.chat.id)
            send_message(update.effective_message, 
                text,
                parse_mode=ParseMode.MARKDOWN)
        else:
            user = context.bot.get_chat(user_id)
            text = tl(update.effective_message, "{}'s id is `{}`.").format(escape_markdown(user.first_name), user.id)
            if update.effective_message.chat.type != "private":
                text += "\n" + tl(update.effective_message, "This group's id is `{}`.").format(update.effective_message.chat.id)
            send_message(update.effective_message, text,
                                                parse_mode=ParseMode.MARKDOWN)
    elif user_id == "error":
        try:
            user = context.bot.get_chat(args[0])
        except BadRequest:
            send_message(update.effective_message, "Error: Unknown User/Chat!")
            return
        text = tl(update.effective_message, "Your id is `{}`.").format(update.effective_message.from_user.id)
        text += "\n" + tl(update.effective_message, "That group's id is `{}`.").format(user.id)
        if update.effective_message.chat.type != "private":
            text += "\n" + tl(update.effective_message, "This group's id is `{}`.").format(update.effective_message.chat.id)
        send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    else:
        chat = update.effective_chat  # type: Optional[Chat]
        if chat.type == "private":
            send_message(update.effective_message, tl(update.effective_message, "Your id is `{}`.").format(update.effective_message.from_user.id),
                                                parse_mode=ParseMode.MARKDOWN)

        else:
            send_message(update.effective_message, tl(update.effective_message, "Your id is `{}`.").format(update.effective_message.from_user.id) + "\n" + tl(update.effective_message, "Id grup ini adalah `{}`.").format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)


@run_async
@spamcheck
def info(update, context):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user_id = extract_user(update.effective_message, args)

    if user_id and user_id != "error":
        user = context.bot.get_chat(user_id)

    elif not msg.reply_to_message and not args:
        user = msg.from_user

    elif not msg.reply_to_message and (not args or (
            len(args) >= 1 and not args[0].startswith("@") and not args[0].isdigit() and not msg.parse_entities(
        [MessageEntity.TEXT_MENTION]))):
        send_message(update.effective_message, tl(update.effective_message, "I can't extract a user from this."))
        return

    else:
        return

    text = tl(update.effective_message, "<b>User info:</b>") \
           + "\nID: <code>{}</code>".format(user.id) + \
           tl(update.effective_message, "\nFirst Name: {}").format(html.escape(user.first_name))

    if user.last_name:
        text += tl(update.effective_message, "\nLast Name: {}").format(html.escape(user.last_name))

    if user.username:
        text += tl(update.effective_message, "\nUsername: @{}").format(html.escape(user.username))

    text += tl(update.effective_message, "\nUser link: {}").format(mention_html(user.id, "link"))

    if user.id == OWNER_ID:
        text += tl(update.effective_message, "\n\nThis person is my owner - I would never do anything against them!")
    else:
        if user.id in SUDO_USERS:
            text += tl(update.effective_message, "\n\nThis person is one of my sudo users! " \
                    "Nearly as powerful as my owner - so watch it.")
        else:
            if user.id in SUPPORT_USERS:
                text += tl(update.effective_message, "\n\nThis person is one of my support users! " \
                        "Not quite a sudo user, but can still gban you off the map.")

            if user.id in WHITELIST_USERS:
                text += tl(update.effective_message, "\n\nThis person has been whitelisted!" \
                        "That means I'm not allowed to ban/kick them.")

    fedowner = feds_sql.get_user_owner_fed_name(user.id)
    if fedowner:
        text += tl(update.effective_message, "\n\nThis user owns the following federations:\n<code>")
        text += "</code>, <code>".join(fedowner)
        text += "</code>"
    # fedadmin = feds_sql.get_user_admin_fed_name(user.id)
    # if fedadmin:
    #     text += tl(update.effective_message, "\n\nThis user is a fed admin in the current federation:\n")
    #     text += ", ".join(fedadmin)

    for mod in USER_INFO:
        mod_info = mod.__user_info__(user.id, chat.id).strip()
        if mod_info:
            text += "\n\n" + mod_info

    send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@run_async
def echo(update, context):
    message = update.effective_message
    chat_id = update.effective_chat.id
    try:
        message.delete()
    except BadRequest:
        pass
    # Advanced
    text, data_type, content, buttons = get_message_type(message)
    tombol = build_keyboard_alternate(buttons)
    if str(data_type) in ('Types.BUTTON_TEXT', 'Types.TEXT'):
        try:
            if message.reply_to_message:
                context.bot.send_message(chat_id, text, parse_mode="markdown", reply_to_message_id=message.reply_to_message.message_id, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(tombol))
            else:
                context.bot.send_message(chat_id, text, quote=False, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(tombol))
        except BadRequest:
            context.bot.send_message(chat_id, tl(update.effective_message, "Wrong markdown text!\nIf you don't know what markdown is, please type `/markdownhelp` in PM."), parse_mode="markdown")
            return


#@run_async
#def sudo_list(update, context):
#    reply = "<b>Sudo Users:</b>\n"
#    for sudo in SUDO_USERS:
#        user_id = int(sudo) # Ensure int
#        user = context.bot.get_chat(user_id)
#        first_name = user.first_name
#        reply += """• <a href="tg://user?id={}">{}</a>\n""".format(user_id, first_name)
#    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


#@run_async
#def support_list(update, context):
#    reply = "<b>Support Users:</b>\n"
#    for support in SUPPORT_USERS:
#        user_id = int(support) # Ensure int
#        user = context.bot.get_chat(user_id)
#        first_name = user.first_name.replace(">", ">")
#        first_name = first_name.replace("<", "<")
#        reply += """• <a href="tg://user?id={}">{}</a>\n""".format(user_id, first_name)
#    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@spamcheck
def markdown_help(update, context):
    send_message(update.effective_message, tl(update.effective_message, "MARKDOWN_HELP").format(dispatcher.bot.first_name), parse_mode=ParseMode.HTML)
    send_message(update.effective_message, tl(update.effective_message, "Try forwarding the following message to me, and you'll see!"))
    send_message(update.effective_message, tl(update.effective_message, "/save test This is a markdown test. _italics_, *bold*, `code`, [URL](example.com) [button](buttonurl:github.com) [button2](buttonurl:google.com:same)"))


@run_async
def stats(update, context):
    update.effective_message.reply_text(
        # This text doesn't get translated as it is internal message.
        "*Current Stats:*\n" + "\n".join([mod.__stats__() for mod in STATS]),
        parse_mode=ParseMode.MARKDOWN)

# /ip is for private use
__help__ = "misc_help"

__mod_name__ = "Misc"


ID_HANDLER = DisableAbleCommandHandler("id", get_id, pass_args=True)
IP_HANDLER = CommandHandler("ip", get_bot_ip, filters=Filters.chat(OWNER_ID))

PASTE_HANDLER = CommandHandler("paste", paste, pass_args=True)
GET_PASTE_HANDLER = CommandHandler("getpaste", get_paste_content, pass_args=True)
PASTE_STATS_HANDLER = CommandHandler("pastestats", get_paste_stats, pass_args=True)

ECHO_HANDLER = CommandHandler("echo", echo, filters=Filters.user(OWNER_ID))
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, filters=Filters.private)
INFO_HANDLER = DisableAbleCommandHandler("info", info, pass_args=True)

#SUDO_LIST_HANDLER = CommandHandler("sudolist", sudo_list, filters=CustomFilters.sudo_filter)
#SUPPORT_LIST_HANDLER = CommandHandler("supportlist", support_list, filters=CustomFilters.sudo_filter)
STATS_HANDLER = CommandHandler("stats", stats, filters=CustomFilters.sudo_filter)

dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
#dispatcher.add_handler(SUDO_LIST_HANDLER)
#dispatcher.add_handler(SUPPORT_LIST_HANDLER)
dispatcher.add_handler(PASTE_HANDLER)
dispatcher.add_handler(GET_PASTE_HANDLER)
dispatcher.add_handler(PASTE_STATS_HANDLER)
dispatcher.add_handler(STATS_HANDLER)
