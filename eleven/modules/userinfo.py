import html
from typing import Optional, List

from telegram import Message, Update, Bot, User
from telegram import ParseMode, MAX_MESSAGE_LENGTH
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import eleven.modules.sql.userinfo_sql as sql
from eleven import dispatcher, SUDO_USERS, spamcheck
from eleven.modules.disable import DisableAbleCommandHandler
from eleven.modules.helper_funcs.extraction import extract_user

from eleven.modules.languages import tl
from eleven.modules.helper_funcs.alternate import send_message


@run_async
@spamcheck
def about_me(update, context):
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    user_id = extract_user(message, args)

    if user_id and user_id != "error":
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_me_info(user.id)

    if info:
        send_message(update.effective_message, "*{}*:\n{}".format(user.first_name, escape_markdown(info)),
                                            parse_mode=ParseMode.MARKDOWN)
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        send_message(update.effective_message, username + tl(update.effective_message, " hasn't set an info message about themselves  yet!"))
    else:
        send_message(update.effective_message, tl(update.effective_message, "You haven't set an info message about yourself yet!"))


@run_async
@spamcheck
def set_about_me(update, context):
    message = update.effective_message  # type: Optional[Message]
    user_id = message.from_user.id
    text = message.text
    info = text.split(None, 1)  # use python's maxsplit to only remove the cmd, hence keeping newlines.
    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            send_message(update.effective_message, tl(update.effective_message, "Updated your info!"))
        else:
            send_message(update.effective_message, 
                tl(update.effective_message, "Your info needs to be under {} characters! You have {}.").format(MAX_MESSAGE_LENGTH // 4, len(info[1])))


@run_async
@spamcheck
def about_bio(update, context):
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    user_id = extract_user(message, args)
    if user_id and user_id != "error":
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_bio(user.id)

    if info:
        send_message(update.effective_message, "*{}*:\n{}".format(user.first_name, escape_markdown(info)),
                                            parse_mode=ParseMode.MARKDOWN)
    elif message.reply_to_message:
        username = user.first_name
        send_message(update.effective_message, tl(update.effective_message, "{} hasn't had a message set about themselves yet!").format(username))
    else:
        send_message(update.effective_message, tl(update.effective_message, "You haven't had a bio set about yourself yet!"))


@run_async
@spamcheck
def set_about_bio(update, context):
    message = update.effective_message  # type: Optional[Message]
    sender = update.effective_user  # type: Optional[User]
    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id
        if user_id == message.from_user.id:
            send_message(update.effective_message, tl(update.effective_message, "Ha, you can't set your own bio! You're at the mercy of others here..."))
            return
        elif user_id == bot.id and sender.id not in SUDO_USERS:
            send_message(update.effective_message, tl(update.effective_message, "Erm... yeah, I only trust sudo users to set my bio."))
            return

        text = message.text
        bio = text.split(None, 1)  # use python's maxsplit to only remove the cmd, hence keeping newlines.
        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                send_message(update.effective_message, tl(update.effective_message, "Updated {}'s bio!").format(repl_message.from_user.first_name))
            else:
                send_message(update.effective_message, 
                    tl(update.effective_message, "A bio needs to be under {} characters! You tried to set {}.").format(
                        MAX_MESSAGE_LENGTH // 4, len(bio[1])))
    else:
        send_message(update.effective_message, tl(update.effective_message, "Reply to someone's message to set their bio!"))


def __user_info__(user_id, chat_id):
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    if bio and me:
        return tl(chat_id, "<b>About user:</b>\n{me}\n<b>What others say:</b>\n{bio}").format(me=me, bio=bio)
    elif bio:
        return tl(chat_id, "<b>What others say:</b>\n{bio}\n").format(me=me, bio=bio)
    elif me:
        return tl(chat_id, "<b>About user:</b>\n{me}").format(me=me, bio=bio)
    else:
        return ""


__help__ = "userinfo_help"

__mod_name__ = "Bios and Abouts"

SET_BIO_HANDLER = DisableAbleCommandHandler("setbio", set_about_bio)
GET_BIO_HANDLER = DisableAbleCommandHandler("bio", about_bio, pass_args=True)

SET_ABOUT_HANDLER = DisableAbleCommandHandler("setme", set_about_me)
GET_ABOUT_HANDLER = DisableAbleCommandHandler("me", about_me, pass_args=True)

dispatcher.add_handler(SET_BIO_HANDLER)
dispatcher.add_handler(GET_BIO_HANDLER)
dispatcher.add_handler(SET_ABOUT_HANDLER)
dispatcher.add_handler(GET_ABOUT_HANDLER)