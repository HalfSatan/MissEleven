import html, time
import re
import threading
import requests
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User, CallbackQuery
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler, run_async, CallbackQueryHandler
from telegram.utils.helpers import mention_markdown, mention_html, escape_markdown

import eleven.modules.sql.welcome_sql as sql
from eleven import dispatcher, OWNER_ID, LOGGER, spamcheck, IS_DEBUG, SUDO_USERS, MESSAGE_DUMP

from eleven.modules.helper_funcs.chat_status import user_admin, is_user_ban_protected, bot_can_restrict
from eleven.modules.helper_funcs.misc import build_keyboard_parser, revert_buttons
from eleven.modules.helper_funcs.msg_types import get_welcome_type
from eleven.modules.helper_funcs.filters import CustomFilters
from eleven.modules.helper_funcs.string_handling import markdown_parser, \
	escape_invalid_curly_brackets, extract_time, make_time
from eleven.modules.helper_funcs.welcome_timeout import welcome_timeout
from eleven.modules.log_channel import loggable

import eleven.modules.sql.feds_sql as fedsql
from eleven.modules.languages import tl
from eleven.modules.helper_funcs.alternate import send_message, leave_chat


OWNER_SPECIAL = True
VALID_WELCOME_FORMATTERS = ['first', 'last', 'fullname', 'username', 'id', 'count', 'chatname', 'mention', 'rules']

ENUM_FUNC_MAP = {
	sql.Types.TEXT.value: dispatcher.bot.send_message,
	sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
	sql.Types.STICKER.value: dispatcher.bot.send_sticker,
	sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
	sql.Types.PHOTO.value: dispatcher.bot.send_photo,
	sql.Types.AUDIO.value: dispatcher.bot.send_audio,
	sql.Types.VOICE.value: dispatcher.bot.send_voice,
	sql.Types.VIDEO.value: dispatcher.bot.send_video
}


# do not async
def send(update, message, keyboard, backup_message):
	chat = update.effective_chat
	cleanserv = sql.clean_service(chat.id)
	reply = update.message.message_id
	# Clean service welcome
	if cleanserv:
		reply = False
	try:
		msg = dispatcher.bot.send_message(chat.id, message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard, reply_to_message_id=reply, disable_web_page_preview=True)
	except IndexError:
		msg = dispatcher.bot.send_message(chat.id, markdown_parser(backup_message +
																  tl(update.effective_message, "\nNote: the current message was invalid due to markdown issues. Could be due to the user's name.")),
												  reply_to_message_id=reply, 
												  parse_mode=ParseMode.MARKDOWN)
	except KeyError:
		msg = dispatcher.bot.send_message(chat.id, markdown_parser(backup_message +
																  tl(update.effective_message, "\nNote: the current message is invalid due to an issue with some misplaced curly brackets. Please update")),
												  reply_to_message_id=reply, 
												  parse_mode=ParseMode.MARKDOWN)
	except BadRequest as excp:
		if excp.message == "Button_url_invalid":
			msg = dispatcher.bot.send_message(chat.id, markdown_parser(backup_message +
																	  tl(update.effective_message, "\nNote: the current message has an invalid url in one of its buttons. Please update.")),
													  reply_to_message_id=reply, 
													  parse_mode=ParseMode.MARKDOWN)
		elif excp.message == "Unsupported url protocol":
			msg = dispatcher.bot.send_message(chat.id, markdown_parser(backup_message +
																	  tl(update.effective_message, "\nNote: the current message has buttons which use url protocols that are unsupported by telegram. Please update.")),
													  reply_to_message_id=reply, 
													  parse_mode=ParseMode.MARKDOWN)
		elif excp.message == "Wrong url host":
			msg = dispatcher.bot.send_message(chat.id, markdown_parser(backup_message +
																	  tl(update.effective_message, "\nNote: the current message has some bad urls. Please update.")),
													  reply_to_message_id=reply, 
													  parse_mode=ParseMode.MARKDOWN)
			LOGGER.warning(message)
			LOGGER.warning(keyboard)
			LOGGER.exception("Could not parse! got invalid url host errors")
		elif excp.message == "Reply message not found":
			msg = dispatcher.bot.send_message(chat.id, message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard, disable_web_page_preview=True)
		else:
			try:
				msg = dispatcher.bot.send_message(chat.id, markdown_parser(backup_message +
																	  tl(update.effective_message, "\nNote: An error occured when sending the custom message. Please update.")),
													  reply_to_message_id=reply, 
													  parse_mode=ParseMode.MARKDOWN)
				LOGGER.exception("ERROR!")
			except BadRequest as err:
				if IS_DEBUG:
					print("Cannot send welcome msg at {} ({})".format(chat.title, chat.id))
				if str(err) == "Have no rights to send a message":
					leave_chat(update.message)
				return ""
	return msg


@run_async
def new_member(update, context):
	chat = update.effective_chat  # type: Optional[Chat]

	should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
	cleanserv = sql.clean_service(chat.id)
	if cleanserv:
		new_members = update.effective_message.new_chat_members
		for new_mem in new_members:
			try:
				dispatcher.bot.delete_message(chat.id, update.message.message_id)
			except BadRequest:
				pass
	if should_welc:
		sent = None
		new_members = update.effective_message.new_chat_members
		for new_mem in new_members:
			# Give the owner a special welcome
			if OWNER_SPECIAL and new_mem.id == OWNER_ID:
				if cleanserv:
					context.bot.send_message(chat.id, tl(update.effective_message, "Master is in the houseeee, let's get this party started! 😆"))
				else:
					send_message(update.effective_message, tl(update.effective_message, "Master is in the houseeee, let's get this party started! 😆"))
				continue

			# Don't welcome yourself
			elif new_mem.id == context.bot.id:
				context.bot.send_message(
					MESSAGE_DUMP,
					"<b>I was added in a group</b>\n" \
					"#AddGroup\n" \
					"<b>Chat name:</b> {}\n" \
					"<b>ID:</b> <code>{}</code>".format(chat.title, chat.id),
					parse_mode=ParseMode.HTML
				)
				context.bot.send_message(chat.id,
								"Thanks for adding me into your group! Don't forgot to checkout the Eleven Official Support (@MissElevenSupport)! And follow my news channel @MissEleven.")

			else:
				# If welcome message is media, send with appropriate function
				if welc_type != sql.Types.TEXT and welc_type != sql.Types.BUTTON_TEXT:
					reply = update.message.message_id
					# Clean service welcome
					if cleanserv:
						reply = False
					# Formatting text
					first_name = new_mem.first_name or "PersonWithNoName"  # edge case of empty name - occurs for some bugs.
					if new_mem.last_name:
						fullname = "{} {}".format(first_name, new_mem.last_name)
					else:
						fullname = first_name
					count = chat.get_members_count()
					mention = mention_markdown(new_mem.id, first_name)
					if new_mem.username:
						username = "@" + escape_markdown(new_mem.username)
					else:
						username = mention
					rules = "https://t.me/" + context.bot.username + "?start=" + str(chat.id)

					if cust_welcome:
						formatted_text = cust_welcome.format(first=escape_markdown(first_name),
											  last=escape_markdown(new_mem.last_name or first_name),
											  fullname=escape_markdown(fullname), username=username, mention=mention,
											  count=count, chatname=escape_markdown(chat.title), id=new_mem.id, rules=rules)
					else:
						formatted_text = ""
					# Build keyboard
					buttons = sql.get_welc_buttons(chat.id)
					keyb = build_keyboard_parser(context.bot, chat.id, buttons)
					getsec, extra_verify, mutetime, timeout, timeout_mode, custom_text = sql.welcome_security(chat.id)

					# If user ban protected don't apply security on him
					if is_user_ban_protected(chat, new_mem.id, chat.get_member(new_mem.id)):
						pass
					elif getsec:
						# If mute time is turned on
						is_clicked = sql.get_chat_userlist(chat.id)
						if mutetime:
							if mutetime[:1] == "0":
								if new_mem.id not in list(is_clicked):
									try:
										context.bot.restrict_chat_member(chat.id, new_mem.id, permissions=ChatPermissions(can_send_messages=False))
										canrest = True
									except BadRequest:
										canrest = False
								else:
									canrest = bot_can_restrict(chat, context.bot.id)
							else:
								if new_mem.id not in list(is_clicked):
									mutetime = extract_time(update.effective_message, mutetime)
									try:
										context.bot.restrict_chat_member(chat.id, new_mem.id, until_date=mutetime, permissions=ChatPermissions(can_send_messages=False))
										canrest = True
									except BadRequest:
										canrest = False
								else:
									canrest = bot_can_restrict(chat, context.bot.id)
						# If security welcome is turned on
						if is_clicked.get(new_mem.id) and is_clicked[new_mem.id] == True:
							sql.add_to_userlist(chat.id, new_mem.id, True)
						else:
							sql.add_to_userlist(chat.id, new_mem.id, False)
						if canrest:
							if new_mem.id not in list(is_clicked):
								keyb.append([InlineKeyboardButton(text=str(custom_text), callback_data="check_bot_({})".format(new_mem.id))])
							elif new_mem.id in list(is_clicked) and is_clicked[new_mem.id] == False:
								keyb.append([InlineKeyboardButton(text=str(custom_text), callback_data="check_bot_({})".format(new_mem.id))])
					keyboard = InlineKeyboardMarkup(keyb)
					# Send message
					try:
						sent = ENUM_FUNC_MAP[welc_type](chat.id, cust_content, caption=formatted_text, reply_markup=keyboard, parse_mode="markdown", reply_to_message_id=reply)
					except BadRequest:
						sent = send_message(update.effective_message, tl(update.effective_message, "Note: An error occurred while sending custom messages. Please update."))
					return
				else:
					# else, move on
					first_name = new_mem.first_name or "PersonWithNoName"  # edge case of empty name - occurs for some bugs.

					if cust_welcome:
						if new_mem.last_name:
							fullname = "{} {}".format(first_name, new_mem.last_name)
						else:
							fullname = first_name
						count = chat.get_members_count()
						mention = mention_markdown(new_mem.id, first_name)
						if new_mem.username:
							username = "@" + escape_markdown(new_mem.username)
						else:
							username = mention
						rules = "https://t.me/" + context.bot.username + "?start=" + str(chat.id)

						valid_format = escape_invalid_curly_brackets(cust_welcome, VALID_WELCOME_FORMATTERS)
						if valid_format:
							res = valid_format.format(first=escape_markdown(first_name),
												  last=escape_markdown(new_mem.last_name or first_name),
												  fullname=escape_markdown(fullname), username=username, mention=mention,
												  count=count, chatname=escape_markdown(chat.title), id=new_mem.id, rules=rules)
						else:
							res = ""
						buttons = sql.get_welc_buttons(chat.id)
						keyb = build_keyboard_parser(context.bot, chat.id, buttons)
					else:
						res = sql.DEFAULT_WELCOME.format(first=first_name)
						keyb = []

					getsec, extra_verify, mutetime, timeout, timeout_mode, custom_text = sql.welcome_security(chat.id)
					
					# If user ban protected don't apply security on him
					if is_user_ban_protected(chat, new_mem.id, chat.get_member(new_mem.id)):
						pass
					elif getsec:
						is_clicked = sql.get_chat_userlist(chat.id)
						if mutetime:
							if mutetime[:1] == "0":
								if new_mem.id not in list(is_clicked):
									try:
										context.bot.restrict_chat_member(chat.id, new_mem.id, permissions=ChatPermissions(can_send_messages=False))
										canrest = True
									except BadRequest:
										canrest = False
								else:
									canrest = bot_can_restrict(chat, context.bot.id)
							else:
								if new_mem.id not in list(is_clicked):
									mutetime = extract_time(update.effective_message, mutetime)
									try:
										context.bot.restrict_chat_member(chat.id, new_mem.id, until_date=mutetime, permissions=ChatPermissions(can_send_messages=False))
										canrest = True
									except BadRequest:
										canrest = False
								else:
									canrest = bot_can_restrict(chat, context.bot.id)
						if is_clicked.get(new_mem.id) and is_clicked[new_mem.id] == True:
							sql.add_to_userlist(chat.id, new_mem.id, True)
						else:
							sql.add_to_userlist(chat.id, new_mem.id, False)
						if canrest:
							if new_mem.id not in list(is_clicked):
								if extra_verify:
									keyb.append([InlineKeyboardButton(text=str(custom_text), url="t.me/{}?start=verify_{}".format(context.bot.username, chat.id))])
								else:
									keyb.append([InlineKeyboardButton(text=str(custom_text), callback_data="check_bot_({})".format(new_mem.id))])
								if timeout != "0":
									sql.add_to_timeout(chat.id, new_mem.id, int(timeout))
							elif new_mem.id in list(is_clicked) and is_clicked[new_mem.id] == False:
								if extra_verify:
									keyb.append([InlineKeyboardButton(text=str(custom_text), url="t.me/{}?start=verify_{}".format(context.bot.username, chat.id))])
								else:
									keyb.append([InlineKeyboardButton(text=str(custom_text), callback_data="check_bot_({})".format(new_mem.id))])
								if timeout != "0":
									sql.add_to_timeout(chat.id, new_mem.id, int(timeout))
					keyboard = InlineKeyboardMarkup(keyb)

					sent = send(update, res, keyboard,
								sql.DEFAULT_WELCOME.format(first=first_name))  # type: Optional[Message]

				
			prev_welc = sql.get_clean_pref(chat.id)
			if prev_welc:
				try:
					if int(prev_welc) != 1:
						context.bot.delete_message(chat.id, prev_welc)
				except BadRequest as excp:
				   pass

				if sent:
					sql.set_clean_welcome(chat.id, sent.message_id)
	"""
	fed_id = fedsql.get_fed_id(chat.id)
	if fed_id == "LordEleven_Support":
		new_members = update.effective_message.new_chat_members
		for new_mem in new_members:
			# SpamWatch Security thread
			t = threading.Thread(target=check_sw, args=(bot, new_mem.id, new_mem, update.effective_message,))
			t.start()
			# CAS Security thread
			t = threading.Thread(target=check_cas, args=(bot, new_mem.id, new_mem, update.effective_message,))
			t.start()
	"""

@run_async
def check_bot_button(update, context):
	chat = update.effective_chat  # type: Optional[Chat]
	user = update.effective_user  # type: Optional[User]
	query = update.callback_query  # type: Optional[CallbackQuery]
	match = re.match(r"check_bot_\((.+?)\)", query.data)
	user_id = int(match.group(1))
	message = update.effective_message  # type: Optional[Message]
	if IS_DEBUG:
		print("-> {} was clicked welcome sec button".format(user.id))

	# This method will unmute user when that user is clicked welc security button
	# It has two method, so select one method. I'm using first method as default.

	# With second script, bot will edit welcome message and remove welcome security button
	# But when muted user in old welcomes, bot will remove that button,
	# and then new member will not have welcome security button.
	# The problem is bot using list of new member which has been muted,
	# and when that user is match, bot will response True and unmute him/her.
	# All we need is using different filter, it easy but old member has muted by
	# welcome security is no longer unmuted on any welcome security button,
	# need to search their welcome button to get unmute.
	# And you will need two decision, unmute specific user or unmute all user
	# who has muted by security button.
	# Also you can remove add_to_userlist and rm_from_userlist script
	# if you want to use second method since it unused.
	# 
	# 
	# Edit 14/03/2020
	# Now welcome security is more secure!
	# When user was clicked welcome, no need to restirect him/her again,
	# And when they're got muted by admins, and want to rejoin group to
	# bypass mute, he/she will not muted again or send 'unmute me' to them.
	# 

	# PLEASE SELECT ONE
	# use """ to set it as comment and disable that script

	# => Use this if you want to unmute user who has muted by welcome security
	"""
	getalluser = sql.get_chat_userlist(chat.id)
	if getalluser and user.id in list(getalluser) and getalluser[user.id] == False:
		try:
			query.answer(text=tl(update.effective_message, "You've been unmuted!"))
		except BadRequest as err:
			print("-> Failed: {}".format(err))
			return
		# Unmute user
		context.bot.restrict_chat_member(chat.id, user.id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
		# sql.rm_from_userlist(chat.id, user.id)
		sql.add_to_userlist(chat.id, user.id, True)
	else:
		print("Not new user")
		if getalluser.get(user.id) and getalluser.get(user.id) == True:
			try:
				query.answer(text=tl(update.effective_message, "You've clicked this before!"))
			except BadRequest as err:
				print("-> Failed: {}".format(err))
				return
		else:
			try:
				query.answer(text=tl(update.effective_message, "You are not a new member!"))
			except BadRequest as err:
				print("-> Failed: {}".format(err))
				return
	"""

	# => Or use this to unmute specific user and remove that security button
	getalluser = sql.get_chat_userlist(chat.id)
	if int(user.id) != int(user_id):
		if IS_DEBUG:
			print("Not that user")
		query.answer(text=tl(update.effective_message, "You are not the intended user!"))
		return
	if getalluser.get(user.id) and getalluser.get(user.id) == True:
		query.answer(text=tl(update.effective_message, "You've clicked this before!"))
		return
	try:
		context.bot.restrict_chat_member(chat.id, user.id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
	except BadRequest as err:
		if not update.effective_chat.get_member(context.bot.id).can_restrict_members:
			query.answer(text=tl(update.effective_message, "I can't restrict people here, ask admin to unmute you!"))
		else:
			query.answer(text="Error: " + str(err.message))
		return
	sql.add_to_userlist(chat.id, user.id, True)
	should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
	# If welcome message is media, send with appropriate function
	if welc_type != sql.Types.TEXT and welc_type != sql.Types.BUTTON_TEXT:
		# Formatting text
		first_name = query.from_user.first_name or "PersonWithNoName"  # edge case of empty name - occurs for some bugs.
		if query.from_user.last_name:
			fullname = "{} {}".format(first_name, query.from_user.last_name)
		else:
			fullname = first_name
		count = chat.get_members_count()
		mention = mention_markdown(query.from_user.id, first_name)
		if query.from_user.username:
			username = "@" + escape_markdown(query.from_user.username)
		else:
			username = mention
		rules = "https://t.me/" + context.bot.username + "?start=" + str(chat.id)

		formatted_text = cust_welcome.format(first=escape_markdown(first_name),
											 last=escape_markdown(query.from_user.last_name or first_name),
											 fullname=escape_markdown(fullname), username=username, mention=mention,
											 count=count, chatname=escape_markdown(chat.title), id=query.from_user.id, rules=rules)
		# Build keyboard
		buttons = sql.get_welc_buttons(chat.id)
		keyb = build_keyboard_parser(context.bot, chat.id, buttons)
		getsec, extra_verify, mutetime, timeout, timeout_mode, custom_text = sql.welcome_security(chat.id)
		keyboard = InlineKeyboardMarkup(keyb)
		# Send message
		try:
			if welc_type != sql.Types.STICKER or welc_type != sql.Types.VOICE:
				context.bot.editMessageCaption(chat.id, message_id=query.message.message_id, caption=formatted_text, reply_markup=keyboard, parse_mode="markdown")
		except BadRequest:
			pass
		query.answer(text=tl(update.effective_message, "You've been unmuted!"))
		return
	# else, move on
	first_name = query.from_user.first_name or "PersonWithNoName"  # edge case of empty name - occurs for some bugs.
	if cust_welcome:
		if query.from_user.last_name:
			fullname = "{} {}".format(first_name, query.from_user.last_name)
		else:
			fullname = first_name
		count = chat.get_members_count()
		mention = mention_markdown(query.from_user.id, first_name)
		if query.from_user.username:
			username = "@" + escape_markdown(query.from_user.username)
		else:
			username = mention
		rules = "https://t.me/" + context.bot.username + "?start=" + str(chat.id)

		valid_format = escape_invalid_curly_brackets(cust_welcome, VALID_WELCOME_FORMATTERS)
		res = valid_format.format(first=escape_markdown(first_name),
								  last=escape_markdown(query.from_user.last_name or first_name),
								  fullname=escape_markdown(fullname), username=username, mention=mention,
								  count=count, chatname=escape_markdown(chat.title), id=query.from_user.id, rules=rules)
		buttons = sql.get_welc_buttons(chat.id)
		keyb = build_keyboard_parser(context.bot, chat.id, buttons)
	else:
		res = sql.DEFAULT_WELCOME.format(first=first_name)
		keyb = []
	keyboard = InlineKeyboardMarkup(keyb)
	context.bot.editMessageText(chat_id=chat.id, message_id=query.message.message_id, text=res, reply_markup=keyboard, parse_mode="markdown")
	query.answer(text=tl(update.effective_message, "You've been unmuted!"))
	#TODO need kick users after 2 hours and remove message 


@run_async
def left_member(update, context):
	chat = update.effective_chat  # type: Optional[Chat]
	should_goodbye, cust_goodbye, cust_content, goodbye_type = sql.get_gdbye_pref(chat.id)
	if should_goodbye:
		left_mem = update.effective_message.left_chat_member
		if left_mem:
			# Ignore bot being kicked
			if left_mem.id == context.bot.id:
				return

			# Give the owner a special goodbye
			if OWNER_SPECIAL and left_mem.id == OWNER_ID:
				send_message(update.effective_message, tl(update.effective_message, "RIP Master 😢"))
				return

			# if media goodbye, use appropriate function for it
			if goodbye_type != sql.Types.TEXT and goodbye_type != sql.Types.BUTTON_TEXT:
				reply = update.message.message_id
				cleanserv = sql.clean_service(chat.id)
				# Clean service welcome
				if cleanserv:
					try:
						dispatcher.bot.delete_message(chat.id, update.message.message_id)
					except BadRequest:
						pass
					reply = False
				# Formatting text
				first_name = left_mem.first_name or "PersonWithNoName"  # edge case of empty name - occurs for some bugs.
				if left_mem.last_name:
					fullname = "{} {}".format(first_name, left_mem.last_name)
				else:
					fullname = first_name
				count = chat.get_members_count()
				mention = mention_markdown(left_mem.id, first_name)
				if left_mem.username:
					username = "@" + escape_markdown(left_mem.username)
				else:
					username = mention
				rules = "https://t.me/" + context.bot.username + "?start=" + str(chat.id)

				if cust_goodbye:
					formatted_text = cust_goodbye.format(first=escape_markdown(first_name),
											  last=escape_markdown(left_mem.last_name or first_name),
											  fullname=escape_markdown(fullname), username=username, mention=mention,
											  count=count, chatname=escape_markdown(chat.title), id=left_mem.id, rules=rules)
				else:
					formatted_text = ""
				# Build keyboard
				buttons = sql.get_gdbye_buttons(chat.id)
				keyb = build_keyboard_parser(context.bot, chat.id, buttons)
				keyboard = InlineKeyboardMarkup(keyb)
				# Send message
				try:
					ENUM_FUNC_MAP[goodbye_type](chat.id, cust_content, caption=formatted_text, reply_markup=keyboard, parse_mode="markdown", reply_to_message_id=reply)
				except BadRequest:
					send_message(update.effective_message, tl(update.effective_message, "Note: An error occurred while sending custom messages. Please update."))
				return

			first_name = left_mem.first_name or "PersonWithNoName"  # edge case of empty name - occurs for some bugs.
			if cust_goodbye:
				if left_mem.last_name:
					fullname = "{} {}".format(first_name, left_mem.last_name)
				else:
					fullname = first_name
				count = chat.get_members_count()
				mention = mention_markdown(left_mem.id, first_name)
				if left_mem.username:
					username = "@" + escape_markdown(left_mem.username)
				else:
					username = mention

				valid_format = escape_invalid_curly_brackets(cust_goodbye, VALID_WELCOME_FORMATTERS)
				if valid_format:
					res = valid_format.format(first=escape_markdown(first_name),
										  last=escape_markdown(left_mem.last_name or first_name),
										  fullname=escape_markdown(fullname), username=username, mention=mention,
										  count=count, chatname=escape_markdown(chat.title), id=left_mem.id)
				else:
					res = ""
				buttons = sql.get_gdbye_buttons(chat.id)
				keyb = build_keyboard_parser(context.bot, chat.id, buttons)

			else:
				res = sql.DEFAULT_GOODBYE
				keyb = []

			keyboard = InlineKeyboardMarkup(keyb)

			send(update, res, keyboard, sql.DEFAULT_GOODBYE)


@run_async
@spamcheck
@user_admin
def security(update, context):
	args = context.args
	chat = update.effective_chat  # type: Optional[Chat]
	getcur, extra_verify, cur_value, timeout, timeout_mode, cust_text = sql.welcome_security(chat.id)
	if len(args) >= 1:
		var = args[0].lower()
		if (var == "yes" or var == "ya" or var == "on"):
			check = context.bot.getChatMember(chat.id, context.bot.id)
			if check.status == 'member' or check['can_restrict_members'] == False:
				text = tl(update.effective_message, "I can't restrict member here! Make sure I'm an admin an can mute someone!")
				send_message(update.effective_message, text, parse_mode="markdown")
				return ""
			sql.set_welcome_security(chat.id, True, extra_verify, str(cur_value), str(timeout), int(timeout_mode), cust_text)
			send_message(update.effective_message, tl(update.effective_message, "Security for new members is activated!"))
		elif (var == "no" or var == "ga" or var == "off"):
			sql.set_welcome_security(chat.id, False, extra_verify, str(cur_value), str(timeout), int(timeout_mode), cust_text)
			send_message(update.effective_message, tl(update.effective_message, "Disabled, I will not mute new member again"))
		else:
			send_message(update.effective_message, tl(update.effective_message, "Please write `on`/`off`!"), parse_mode=ParseMode.MARKDOWN)
	else:
		getcur, extra_verify, cur_value, timeout, timeout_mode, cust_text = sql.welcome_security(chat.id)
		if cur_value[:1] == "0":
			cur_value = tl(update.effective_message, "Forever")
		text = tl(update.effective_message, "Current settings are:\nWelcome security: `{}`\nVerify security: `{}`\nMembers will be muted for: `{}`\nVerification timeout: `{}`\nUnmute custom button: `{}`").format(getcur, extra_verify, cur_value, make_time(int(timeout)), "kick" if 1 else "banned", cust_text)
		send_message(update.effective_message, text, parse_mode="markdown")


@run_async
@spamcheck
@user_admin
def security_mute(update, context):
	args = context.args
	chat = update.effective_chat  # type: Optional[Chat]
	message = update.effective_message  # type: Optional[Message]
	getcur, extra_verify, cur_value, timeout, timeout_mode, cust_text = sql.welcome_security(chat.id)
	if len(args) >= 1:
		var = args[0]
		if var[:1] == "0":
			mutetime = "0"
			sql.set_welcome_security(chat.id, getcur, extra_verify, "0", timeout, timeout_mode, cust_text)
			text = tl(update.effective_message, "Every new member will be muted forever until they presses the welcome button!")
		else:
			mutetime = extract_time(message, var)
			if mutetime == "":
				return
			sql.set_welcome_security(chat.id, getcur, extra_verify, str(var), timeout, timeout_mode, cust_text)
			text = tl(update.effective_message, "Every new member will be muted for {} until they presses the welcome button!").format(var)
		send_message(update.effective_message, text)
	else:
		if str(cur_value) == "0":
			send_message(update.effective_message, tl(update.effective_message, "Current settings: new member will be muted forever until they presses the welcome button!"))
		else:
			send_message(update.effective_message, tl(update.effective_message, "Current settings: new member will be muted for {} until they presses the welcome button!").format(cur_value))


@run_async
@spamcheck
@user_admin
def security_text(update, context):
	args = context.args
	chat = update.effective_chat  # type: Optional[Chat]
	message = update.effective_message  # type: Optional[Message]
	getcur, extra_verify, cur_value, timeout, timeout_mode, cust_text = sql.welcome_security(chat.id)
	if len(args) >= 1:
		text = " ".join(args)
		sql.set_welcome_security(chat.id, getcur, extra_verify, cur_value, timeout, timeout_mode, text)
		text = tl(update.effective_message, "Custom text button has been changed to: `{}`").format(text)
		send_message(update.effective_message, text, parse_mode="markdown")
	else:
		send_message(update.effective_message, tl(update.effective_message, "Current custom text button is: `{}`").format(cust_text), parse_mode="markdown")


@run_async
@spamcheck
@user_admin
def security_text_reset(update, context):
	chat = update.effective_chat  # type: Optional[Chat]
	message = update.effective_message  # type: Optional[Message]
	getcur, extra_verify, cur_value, timeout, timeout_mode, cust_text = sql.welcome_security(chat.id)
	sql.set_welcome_security(chat.id, getcur, extra_verify, cur_value, timeout, timeout_mode, tl(update.effective_message, "Click here to unmute"))
	send_message(update.effective_message, tl(update.effective_message, "Custom text security button has been reset to: `Click here to unmute`"), parse_mode="markdown")


@run_async
@spamcheck
@user_admin
def cleanservice(update, context):
	args = context.args
	chat = update.effective_chat  # type: Optional[Chat]
	if chat.type != chat.PRIVATE:
		if len(args) >= 1:
			var = args[0].lower()
			if (var == "no" or var == "off" or var == "tidak"):
				sql.set_clean_service(chat.id, False)
				send_message(update.effective_message, tl(update.effective_message, "I left a service message"))
			elif(var == "yes" or var == "ya" or var == "on"):
				sql.set_clean_service(chat.id, True)
				send_message(update.effective_message, tl(update.effective_message, "I will clean the service message"))
			else:
				send_message(update.effective_message, tl(update.effective_message, "Please enter yes or no!"), parse_mode=ParseMode.MARKDOWN)
		else:
			send_message(update.effective_message, tl(update.effective_message, "Please enter yes or no!"), parse_mode=ParseMode.MARKDOWN)
	else:
		curr = sql.clean_service(chat.id)
		if curr:
			send_message(update.effective_message, tl(update.effective_message, "At this time I will clean `x joined the group` when there is a new member."), parse_mode=ParseMode.MARKDOWN)
		else:
			send_message(update.effective_message, tl(update.effective_message, "At this time I will not clean `x joined the group` when there is a new member."), parse_mode=ParseMode.MARKDOWN)



@run_async
@user_admin
def welcome(update, context):
	chat = update.effective_chat  # type: Optional[Chat]
	args = context.args
	# if no args, show current replies.
	if len(args) == 0 or args[0].lower() == "noformat":
		noformat = args and args[0].lower() == "noformat"
		pref, welcome_m, cust_content, welcome_type = sql.get_welc_pref(chat.id)
		prev_welc = sql.get_clean_pref(chat.id)
		if prev_welc:
			prev_welc = True
		else:
			prev_welc = False
		cleanserv = sql.clean_service(chat.id)
		getcur, extra_verify, cur_value, timeout, timeout_mode, cust_text = sql.welcome_security(chat.id)
		if getcur:
			welcsec = tl(update.effective_message, "Enabled ")
		else:
			welcsec = tl(update.effective_message, "Disabled ")
		if cur_value[:1] == "0":
			welcsec += tl(update.effective_message, "(mute forever until pressing the unmute button)")
		else:
			welcsec += tl(update.effective_message, "(muted for {})").format(cur_value)
		text = tl(update.effective_message, "This chat is set with a welcome setting: `{}`\n").format(pref)
		text += tl(update.effective_message, "At this time I deleted the old welcome message: `{}`\n").format(prev_welc)
		text += tl(update.effective_message, "I am currently deleting the message service: `{}`\n").format(cleanserv)
		text += tl(update.effective_message, "Currently I mute users when they join: `{}`\n").format(welcsec)
		text += tl(update.effective_message, "New users must verify: `{}`\n").format(tl(update.effective_message, "Enabled ") if extra_verify else tl(update.effective_message, "Disabled "))
		text += tl(update.effective_message, "The button welcomemute will say: `{}`\n").format(cust_text)
		text += tl(update.effective_message, "\n*Welcome message (not filling the {{}}) is:*")
		send_message(update.effective_message, text,
			parse_mode=ParseMode.MARKDOWN)

		buttons = sql.get_welc_buttons(chat.id)
		if welcome_type == sql.Types.BUTTON_TEXT or welcome_type == sql.Types.TEXT:
			if noformat:
				welcome_m += revert_buttons(buttons)
				send_message(update.effective_message, welcome_m)

			else:
				if buttons:
					keyb = build_keyboard_parser(context.bot, chat.id, buttons)
					keyboard = InlineKeyboardMarkup(keyb)
				else:
					keyboard = None

				send(update, welcome_m, keyboard, sql.DEFAULT_WELCOME)

		else:
			if noformat:
				welcome_m += revert_buttons(buttons)
				ENUM_FUNC_MAP[welcome_type](chat.id, cust_content, caption=welcome_m)

			else:
				if buttons:
					keyb = build_keyboard_parser(context.bot, chat.id, buttons)
					keyboard = InlineKeyboardMarkup(keyb)
				else:
					keyboard = None
				ENUM_FUNC_MAP[welcome_type](chat.id, cust_content, caption=welcome_m, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

	elif len(args) >= 1:
		if args[0].lower() in ("on", "yes"):
			sql.set_welc_preference(str(chat.id), True)
			send_message(update.effective_message, tl(update.effective_message, "I'll be polite! 😁"))

		elif args[0].lower() in ("off", "no"):
			sql.set_welc_preference(str(chat.id), False)
			send_message(update.effective_message, tl(update.effective_message, "I'm sulking, not saying hello anymore. 😣"))

		else:
			# idek what you're writing, say yes or no
			send_message(update.effective_message, tl(update.effective_message, "I only understand 'on/yes' or 'off/no' only!"))


@run_async
@user_admin
def goodbye(update, context):
	chat = update.effective_chat  # type: Optional[Chat]
	args = context.args

	if len(args) == 0 or args[0] == "noformat":
		noformat = args and args[0] == "noformat"
		pref, goodbye_m, cust_content, goodbye_type = sql.get_gdbye_pref(chat.id)
		send_message(update.effective_message, 
			tl(update.effective_message, "This chat has it's goodbye setting set to: `{}`.\n*The goodbye  message (not filling the {{}}) is:*").format(pref),
			parse_mode=ParseMode.MARKDOWN)

		buttons = sql.get_gdbye_buttons(chat.id)
		if goodbye_type == sql.Types.TEXT or goodbye_type == sql.Types.BUTTON_TEXT:
			if noformat:
				goodbye_m += revert_buttons(buttons)
				send_message(update.effective_message, goodbye_m)

			else:
				if buttons:
					keyb = build_keyboard_parser(context.bot, chat.id, buttons)
					keyboard = InlineKeyboardMarkup(keyb)
				else:
					keyboard = None

				send(update, goodbye_m, keyboard, sql.DEFAULT_GOODBYE)

		else:
			if noformat:
				goodbye_m += revert_buttons(buttons)
				ENUM_FUNC_MAP[goodbye_type](chat.id, cust_content, caption=goodbye_m)
				
			else:
				if buttons:
					keyb = build_keyboard_parser(context.bot, chat.id, buttons)
					keyboard = InlineKeyboardMarkup(keyb)
				else:
					keyboard = None
				ENUM_FUNC_MAP[goodbye_type](chat.id, cust_content, caption=goodbye_m, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

	elif len(args) >= 1:
		if args[0].lower() in ("on", "yes"):
			sql.set_gdbye_preference(str(chat.id), True)
			send_message(update.effective_message, tl(update.effective_message, "I'll be sorry when people leave!"))

		elif args[0].lower() in ("off", "no"):
			sql.set_gdbye_preference(str(chat.id), False)
			send_message(update.effective_message, tl(update.effective_message, "They leave, they're dead to me."))

		else:
			# idk what you're writing, say yes or no
			send_message(update.effective_message, tl(update.effective_message, "I only understand 'on/yes' or 'off/no' only!"))


@run_async
@spamcheck
@user_admin
@loggable
def set_welcome(update, context) -> str:
	chat = update.effective_chat  # type: Optional[Chat]
	user = update.effective_user  # type: Optional[User]
	msg = update.effective_message  # type: Optional[Message]

	# If user is not set text and not reply a message
	if not msg.reply_to_message:
		if len(msg.text.split()) == 1:
			send_message(update.effective_message, tl(update.effective_message, "You must provide the contents in the welcome message!\nType `/welcomehelp` to get some help on welcome"), parse_mode="markdown")
			return ""

	text, data_type, content, buttons = get_welcome_type(msg)

	if data_type is None:
		send_message(update.effective_message, tl(update.effective_message, "You didn't specify what to reply with!"))
		return ""

	sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
	send_message(update.effective_message, tl(update.effective_message, "Successfully set a custom welcome message!"))

	return "<b>{}:</b>" \
		   "\n#SET_WELCOME" \
		   "\n<b>Admin:</b> {}" \
		   "\nSet a welcome message.".format(html.escape(chat.title),
											   mention_html(user.id, user.first_name))


@run_async
@spamcheck
@user_admin
@loggable
def reset_welcome(update, context) -> str:
	chat = update.effective_chat  # type: Optional[Chat]
	user = update.effective_user  # type: Optional[User]
	sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, sql.Types.TEXT)
	send_message(update.effective_message, tl(update.effective_message, "Successfully reset the welcome message to default!"))
	return "<b>{}:</b>" \
		   "\n#RESET_WELCOME" \
		   "\n<b>Admin:</b> {}" \
		   "\nReset the welcome message to default.".format(html.escape(chat.title),
															mention_html(user.id, user.first_name))


@run_async
@spamcheck
@user_admin
@loggable
def set_goodbye(update, context) -> str:
	chat = update.effective_chat  # type: Optional[Chat]
	user = update.effective_user  # type: Optional[User]
	msg = update.effective_message  # type: Optional[Message]

	# If user is not set text and not reply a message
	if not msg.reply_to_message:
		if len(msg.text.split()) == 1:
			send_message(update.effective_message, tl(update.effective_message, "You must provide the contents in the welcome message!\nType `/welcomehelp` to get some help on welcome"), parse_mode="markdown")
			return ""

	text, data_type, content, buttons = get_welcome_type(msg)

	if data_type is None:
		send_message(update.effective_message, tl(update.effective_message, "You didn't specify what to reply with!"))
		return ""

	sql.set_custom_gdbye(chat.id, content, text, data_type, buttons)
	send_message(update.effective_message, tl(update.effective_message, "Successfully set custom goodbye messages!"))
	return "<b>{}:</b>" \
		   "\n#SET_GOODBYE" \
		   "\n<b>Admin:</b> {}" \
		   "\nSet a goodbye message.".format(html.escape(chat.title),
											   mention_html(user.id, user.first_name))


@run_async
@spamcheck
@user_admin
@loggable
def reset_goodbye(update, context) -> str:
	chat = update.effective_chat  # type: Optional[Chat]
	user = update.effective_user  # type: Optional[User]
	sql.set_custom_gdbye(chat.id, sql.DEFAULT_GOODBYE, sql.Types.TEXT)
	send_message(update.effective_message, tl(update.effective_message, "Successfully reset goodbye message to default!"))
	return "<b>{}:</b>" \
		   "\n#RESET_GOODBYE" \
		   "\n<b>Admin:</b> {}" \
		   "\nSetel ulang pesan selamat tinggal.".format(html.escape(chat.title),
												 mention_html(user.id, user.first_name))


@run_async
@spamcheck
@user_admin
@loggable
def clean_welcome(update, context):
	chat = update.effective_chat  # type: Optional[Chat]
	user = update.effective_user  # type: Optional[User]
	args = context.args

	if not args:
		clean_pref = sql.get_clean_pref(chat.id)
		if clean_pref:
			send_message(update.effective_message, tl(update.effective_message, "I should be deleting welcome messages up to two days old."), parse_mode="markdown")
		else:
			send_message(update.effective_message, tl(update.effective_message, "I'm currently not deleting old welcome messages!"), parse_mode="markdown")
		return ""

	if args[0].lower() in ("on", "yes"):
		sql.set_clean_welcome(str(chat.id), True)
		send_message(update.effective_message, tl(update.effective_message, "I'll try to delete old welcome messages!"), parse_mode="markdown")
		return "<b>{}:</b>" \
			   "\n#CLEAN_WELCOME" \
			   "\n<b>Admin:</b> {}" \
			   "\nHas toggled clean welcomes to <code>ON</code>.".format(html.escape(chat.title),
																							 mention_html(user.id, user.first_name))
	elif args[0].lower() in ("off", "no"):
		sql.set_clean_welcome(str(chat.id), False)
		send_message(update.effective_message, tl(update.effective_message, "I won't delete old welcome messages."), parse_mode="markdown")
		return "<b>{}:</b>" \
			   "\n#CLEAN_WELCOME" \
			   "\n<b>Admin:</b> {}" \
			   "\nHas toggled clean welcomes to <code>OFF</code>.".format(html.escape(chat.title),
																		  mention_html(user.id, user.first_name))
	else:
		# idk what you're writing, say yes or no
		send_message(update.effective_message, tl(update.effective_message, "I only understand 'on/yes' or 'off/no' only!"))
		return ""


@run_async
@spamcheck
@user_admin
def welcome_help(update, context):
	send_message(update.effective_message, tl(update.effective_message, "WELC_HELP_TXT").format(dispatcher.bot.username), parse_mode=ParseMode.MARKDOWN)


# TODO: get welcome data from group butler snap
# def __import_data__(chat_id, data):
#     welcome = data.get('info', {}).get('rules')
#     welcome = welcome.replace('$username', '{username}')
#     welcome = welcome.replace('$name', '{fullname}')
#     welcome = welcome.replace('$id', '{id}')
#     welcome = welcome.replace('$title', '{chatname}')
#     welcome = welcome.replace('$surname', '{lastname}')
#     welcome = welcome.replace('$rules', '{rules}')
#     sql.set_custom_welcome(chat_id, welcome, sql.Types.TEXT)


def __migrate__(old_chat_id, new_chat_id):
	sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
	welcome_pref, _, _, _ = sql.get_welc_pref(chat_id)
	goodbye_pref, _, _, _ = sql.get_gdbye_pref(chat_id)
	cleanserv = sql.clean_service(chat_id)
	return tl(user_id, "This chat has a `{}` preference for welcome messages.\nFor goodbye preferences `{}`.\nBot `{}` automatically removes incoming/outgoing member notifications").format(welcome_pref, goodbye_pref, cleanserv)

"""
def __chat_settings_btn__(chat_id, user_id):
	welcome_pref, _, _, _ = sql.get_welc_pref(chat_id)
	goodbye_pref, _, _, _ = sql.get_gdbye_pref(chat_id)
	cleanserv = sql.clean_service(chat_id)
	if welcome_pref:
		welc = "✅ enabled"
	else:
		welc = "❎ disabled"
	if goodbye_pref:
		gdby = "✅ enabled"
	else:
		gdby = "❎ disabled"
	if cleanserv:
		clserv = "✅ enabled"
	else:
		clserv = "❎ disabled"
	button = []
	button.append([InlineKeyboardButton(text="Welcome", callback_data="set_welc=w?|{}".format(chat_id)),
		InlineKeyboardButton(text=welc, callback_data="set_welc=w|{}".format(chat_id))])
	button.append([InlineKeyboardButton(text="Goodbye", callback_data="set_welc=g?|{}".format(chat_id)),
		InlineKeyboardButton(text=gdby, callback_data="set_welc=g|{}".format(chat_id))])
	button.append([InlineKeyboardButton(text="Clean Service", callback_data="set_welc=s?|{}".format(chat_id)),
		InlineKeyboardButton(text=clserv, callback_data="set_welc=s|{}".format(chat_id))])
	return button

def WELC_EDITBTN(update, context):
	query = update.callback_query
	user = update.effective_user
	print("User {} clicked button WELC EDIT".format(user.id))
	chat_id = query.data.split("|")[1]
	data = query.data.split("=")[1].split("|")[0]
	if data == "w?":
		context.bot.answerCallbackQuery(query.id, "Bots will send a message every time a new member enters if activated.", show_alert=True)
	if data == "g?":
		context.bot.answerCallbackQuery(query.id, "The bot will send a message every time a member leaves if activated. Will be active only for groups under 100 members.", show_alert=True)
	if data == "s?":
		context.bot.answerCallbackQuery(query.id, "Bot will delete notification of member entry or member exit automatically if activated.", show_alert=True)
	if data == "w":
		welcome_pref, _, _, _ = sql.get_welc_pref(chat_id)
		goodbye_pref, _, _, _ = sql.get_gdbye_pref(chat_id)
		cleanserv = sql.clean_service(chat_id)
		if welcome_pref:
			welc = "❎ disabled"
			sql.set_welc_preference(str(chat_id), False)
		else:
			welc = "✅ enabled"
			sql.set_welc_preference(str(chat_id), True)
		if goodbye_pref:
			gdby = "✅ enabled"
		else:
			gdby = "❎ disabled"
		if cleanserv:
			clserv = "✅ enabled"
		else:
			clserv = "❎ disabled"
		chat = context.bot.get_chat(chat_id)
		text = "*{}* has the following settings for the module *Welcomes/Goodbyes*:\n\n".format(escape_markdown(chat.title))
		text += "This chat preference of the welcome message has been changed to `{}`.\n".format(welc)
		text += "For the message preferences goodbye `{}`.\n".format(gdby)
		text += "Bot `{}` removes incoming/outgoing member notifications automatically".format(clserv)
		button = []
		button.append([InlineKeyboardButton(text="Welcome", callback_data="set_welc=w?|{}".format(chat_id)),
			InlineKeyboardButton(text=welc, callback_data="set_welc=w|{}".format(chat_id))])
		button.append([InlineKeyboardButton(text="Goodbye", callback_data="set_welc=g?|{}".format(chat_id)),
			InlineKeyboardButton(text=gdby, callback_data="set_welc=g|{}".format(chat_id))])
		button.append([InlineKeyboardButton(text="Clean Service", callback_data="set_welc=s?|{}".format(chat_id)),
			InlineKeyboardButton(text=clserv, callback_data="set_welc=s|{}".format(chat_id))])
		button.append([InlineKeyboardButton(text="Back", callback_data="stngs_back({})".format(chat_id))])
		query.message.edit_text(text=text,
								  parse_mode=ParseMode.MARKDOWN,
								  reply_markup=InlineKeyboardMarkup(button))
		context.bot.answer_callback_query(query.id)
	if data == "g":
		welcome_pref, _, _, _ = sql.get_welc_pref(chat_id)
		goodbye_pref, _, _, _ = sql.get_gdbye_pref(chat_id)
		cleanserv = sql.clean_service(chat_id)
		if welcome_pref:
			welc = "✅ enabled"
		else:
			welc = "❎ disabled"
		if goodbye_pref:
			gdby = "❎ disabled"
			sql.set_gdbye_preference(str(chat_id), False)
		else:
			gdby = "✅ enabled"
			sql.set_gdbye_preference(str(chat_id), True)
		if cleanserv:
			clserv = "✅ enabled"
		else:
			clserv = "❎ disabled"
		chat = context.bot.get_chat(chat_id)
		text = "*{}* has the following settings for the module *Welcomes/Goodbyes*:\n\n".format(escape_markdown(chat.title))
		text += "This chat goodbye message preference has been changed to `{}`.\n".format(gdby)
		text += "For the welcome message preference `{}`.\n".format(welc)
		text += "Bot `{}` removes incoming/outgoing member notifications automatically".format(clserv)
		button = []
		button.append([InlineKeyboardButton(text="Welcome", callback_data="set_welc=w?|{}".format(chat_id)),
			InlineKeyboardButton(text=welc, callback_data="set_welc=w|{}".format(chat_id))])
		button.append([InlineKeyboardButton(text="Goodbye", callback_data="set_welc=g?|{}".format(chat_id)),
			InlineKeyboardButton(text=gdby, callback_data="set_welc=g|{}".format(chat_id))])
		button.append([InlineKeyboardButton(text="Clean Service", callback_data="set_welc=s?|{}".format(chat_id)),
			InlineKeyboardButton(text=clserv, callback_data="set_welc=s|{}".format(chat_id))])
		button.append([InlineKeyboardButton(text="Back", callback_data="stngs_back({})".format(chat_id))])
		query.message.edit_text(text=text,
								  parse_mode=ParseMode.MARKDOWN,
								  reply_markup=InlineKeyboardMarkup(button))
		context.bot.answer_callback_query(query.id)
	if data == "s":
		welcome_pref, _, _, _ = sql.get_welc_pref(chat_id)
		goodbye_pref, _, _, _ = sql.get_gdbye_pref(chat_id)
		cleanserv = sql.clean_service(chat_id)
		if welcome_pref:
			welc = "✅ enabled"
		else:
			welc = "❎ disabled"
		if goodbye_pref:
			gdby = "✅ enabled"
		else:
			gdby = "❎ disabled"
		if cleanserv:
			clserv = "❎ disabled"
			sql.set_clean_service(chat_id, False)
		else:
			clserv = "✅ enabled"
			sql.set_clean_service(chat_id, True)
		chat = context.bot.get_chat(chat_id)
		text = "*{}* has the following settings for the module *Welcomes/Goodbyes*:\n\n".format(escape_markdown(chat.title))
		text += "Clean service settings have been changed. Bot `{}` removes incoming/outgoing member notifications.\n".format(clserv)
		text += "For the welcome message preference `{}`.\n".format(welc)
		text += "For the `{}` goodbye preference message.".format(gdby)
		button = []
		button.append([InlineKeyboardButton(text="Welcome", callback_data="set_welc=w?|{}".format(chat_id)),
			InlineKeyboardButton(text=welc, callback_data="set_welc=w|{}".format(chat_id))])
		button.append([InlineKeyboardButton(text="Goodbye", callback_data="set_welc=g?|{}".format(chat_id)),
			InlineKeyboardButton(text=gdby, callback_data="set_welc=g|{}".format(chat_id))])
		button.append([InlineKeyboardButton(text="Clean Service", callback_data="set_welc=s?|{}".format(chat_id)),
			InlineKeyboardButton(text=clserv, callback_data="set_welc=s|{}".format(chat_id))])
		button.append([InlineKeyboardButton(text="Back", callback_data="stngs_back({})".format(chat_id))])
		query.message.edit_text(text=text,
								  parse_mode=ParseMode.MARKDOWN,
								  reply_markup=InlineKeyboardMarkup(button))
		context.bot.answer_callback_query(query.id)
"""

__help__ = "welcome_help"

__mod_name__ = "Greetings"

NEW_MEM_HANDLER = MessageHandler(Filters.status_update.new_chat_members, new_member)
LEFT_MEM_HANDLER = MessageHandler(Filters.status_update.left_chat_member, left_member)
WELC_PREF_HANDLER = CommandHandler("welcome", welcome, pass_args=True, filters=Filters.group)
GOODBYE_PREF_HANDLER = CommandHandler("goodbye", goodbye, pass_args=True, filters=Filters.group)
SET_WELCOME = CommandHandler("setwelcome", set_welcome, filters=Filters.group)
SET_GOODBYE = CommandHandler("setgoodbye", set_goodbye, filters=Filters.group)
RESET_WELCOME = CommandHandler("resetwelcome", reset_welcome, filters=Filters.group)
RESET_GOODBYE = CommandHandler("resetgoodbye", reset_goodbye, filters=Filters.group)
CLEAN_WELCOME = CommandHandler("cleanwelcome", clean_welcome, pass_args=True, filters=Filters.group)
WELCOME_HELP = CommandHandler("welcomehelp", welcome_help)
SECURITY_HANDLER = CommandHandler("welcomemute", security, pass_args=True, filters=Filters.group)
SECURITY_MUTE_HANDLER = CommandHandler("welcomemutetime", security_mute, pass_args=True, filters=Filters.group)
SECURITY_BUTTONTXT_HANDLER = CommandHandler("setmutetext", security_text, pass_args=True, filters=Filters.group)
SECURITY_BUTTONRESET_HANDLER = CommandHandler("resetmutetext", security_text_reset, filters=Filters.group)
CLEAN_SERVICE_HANDLER = CommandHandler("cleanservice", cleanservice, pass_args=True, filters=Filters.group)

welcomesec_callback_handler = CallbackQueryHandler(check_bot_button, pattern=r"check_bot_")
# WELC_BTNSET_HANDLER = CallbackQueryHandler(WELC_EDITBTN, pattern=r"set_welc")

dispatcher.add_handler(NEW_MEM_HANDLER)
dispatcher.add_handler(LEFT_MEM_HANDLER)
dispatcher.add_handler(WELC_PREF_HANDLER)
dispatcher.add_handler(GOODBYE_PREF_HANDLER)
dispatcher.add_handler(SET_WELCOME)
dispatcher.add_handler(SET_GOODBYE)
dispatcher.add_handler(RESET_WELCOME)
dispatcher.add_handler(RESET_GOODBYE)
dispatcher.add_handler(CLEAN_WELCOME)
dispatcher.add_handler(WELCOME_HELP)
dispatcher.add_handler(SECURITY_HANDLER)
dispatcher.add_handler(SECURITY_MUTE_HANDLER)
dispatcher.add_handler(SECURITY_BUTTONTXT_HANDLER)
dispatcher.add_handler(SECURITY_BUTTONRESET_HANDLER)
dispatcher.add_handler(CLEAN_SERVICE_HANDLER)

dispatcher.add_handler(welcomesec_callback_handler)
#dispatcher.add_handler(WELC_BTNSET_HANDLER)
