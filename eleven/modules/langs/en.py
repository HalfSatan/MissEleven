__lang__ = "🇺🇸 English"

en = {
# main stuff
	"start_text": """
Hi {}, my name is {}! I am a group manager managed by [my master](tg://user?id={}).
To get this bot status info and update, you can join our channel [Eleven Bot News](https://t.me/MissEleven)

Any issue or need more help?
Join our group [Eleven Official Support](https://t.me/MissElevenSupport)!

You can find the list of available commands with /help.

If you're enjoying using me, and/or would like to help me survive in the wild, hit /donate to help fund/upgrade my VPS!
""",
	"help_text": """
Hey there! My name is *Eleven*.
I'm a modular group management bot with a few fun extras! Have a look at the following for an idea of some of \
the things I can help you with.

*Main* commands available:
 - /start: start the bot
 - /help: PM's you this message.
 - /help <module name>: PM's you info about that module.
 - /donate: information about how to donate!
 - /settings:
   - in PM: will send you your settings for all supported modules.
   - in a group: will redirect you to pm, with all that chat's settings.


All commands can either be used with / or !.

And the following:
""",
	"donate_text": """Hello, glad to hear you want to donate!
Need a lot of work for [my creator](tg://user?id=834309762) to take me to my place now, and \
every donation helps and motivates him to make me better.

All donated money will be given to a better VPS to host me, and or some food. \
He is just an ordinary person, so it will really help him!

Thank you 😁""",
	
# Help modules
	"language_help": """Not every group speaks indonesian; some groups would rather have Eleven respond in their own language.

This is where translations come in; you can change most of Eleven's replies to be in the language of your choice!

Available languages are:
- 🇺🇸 English
- 🇮🇩 Indonesia

Available commands are:
 - /setlang: set your prefered language.""",

	"admin_help": """
 - /adminlist | /admins: list of admins in the chat
*Admin only:*
 - /pin: silently pins the message replied to - add 'loud' or 'notify' to give notifs to users.
 - /unpin: unpins the currently pinned message
 - /permapin <teks>: Pin a custom messages via bots. This message can contain markdown, and can be used in replies to the media include additional buttons and text.
 - /permanentpin: Set a permanent pin for supergroup chat, when an admin or telegram channel change pinned message, bot will change pinned message immediatelly
 - /invitelink: gets invitelink
 - /promote: promotes the user replied to
 - /demote: demotes the user replied to
""",
	"afk_help": """
 - /afk <reason>: mark yourself as AFK.
 - brb <reason>: same as the afk command - but not a command.

When marked as AFK, any mentions will be replied to with a message to say you're not available!
""",
	"antiflood_help": """
 - /flood: Get the current flood control setting

*Admin only:*
 - /setflood <int/'no'/'off'>: enables or disables flood control
 - /setfloodmode <ban/kick/mute/tban/tmute> <value>: select the action perform when warnings have been exceeded. ban/kick/mute/tmute/tban

 Note:
 - Value must be filled for tban and tmute, Can be:
	`4m` = 4 minutes
	`3h` = 4 hours
	`2d` = 2 days
	`1w` = 1 week
""",
	
	"urlblacklist_help": """
Domain blacklisting is used to stop certain domains from being mentioned in a group, Any time an url on that domain is mentioned, /
the message will immediately be deleted.

*NOTE:* domain blacklisting do not affect group admins.

- /geturl: View the current blacklisted urls

*Admin only:*

- /addurl <urls>: Add a domain to the blacklist. The bot will automatically parse the url.
- /delurl <urls>: Remove urls from the blacklist
""",	

# Direct Links
	"directlinks_help": """
*This module allows you to generate direct links from various websites.*

/direct <url>: paste a URL to generate a direct download link.

*List of supported URLs:*
`Google Drive - MediaFire - SourceForge`
""",	
	
	"backups_help": """
*Admin only:*
 - /import: reply to a group butler/marie/rose/diablo backup file to import as much as possible, making the transfer super simple!
Note that files/photos from other bots can't be imported due to telegram restrictions. Except for Eleven backup it self.
 - /export: export group data, you can do this 12 hours once.
""",
	
	"bans_help": """
 - /kickme: kicks the user who issued the command

*Admin only:*
 - /ban <userhandle>: bans a user. (via handle, or reply)
 - /sban <userhandle>: silent ban a user, bot will not reply and delete your sban message.
 - /tban <userhandle> x(m/h/d): bans a user for x time. (via handle, or reply). m = minutes, h = hours, d = days.
 - /unban <userhandle>: unbans a user. (via handle, or reply)
 - /kick <userhandle>: kicks a user, (via handle, or reply)
 - /skick <userhandle>: silent kick a user, bot will not reply and delete your skick message.
""",
	"blacklist_help": """
Blacklists are used to stop certain triggers from being said in a group. Any time the trigger is mentioned, \
the message will immediately be deleted. A good combo is sometimes to pair this up with warn filters!

*NOTE:* blacklists do not affect group admins.
 - /blacklist: View the current blacklisted words.

*Admin only:*
 - /addblacklist <triggers>: Add a trigger to the blacklist. Each line is considered one trigger, so using different \
lines will allow you to add multiple triggers.
 - /unblacklist <triggers>: Remove triggers from the blacklist. Same newline logic applies here, so you can remove \
multiple triggers at once.
 - /rmblacklist <triggers>: Same as above.
""",
	"blstickers_help": """
Blacklist sticker is used to stop certain stickers. Whenever a sticker is sent, the message will be deleted immediately.

*NOTE:* Blacklist stickers do not affect the group admin.

 - /blsticker: See current blacklisted sticker.

*Only admin:*
 - /addblsticker <sticker link>: Add the sticker trigger to the black list. Can be added via reply sticker.
 - /unblsticker <sticker link>: Remove triggers from blacklist. The same newline logic applies here, so you can delete multiple triggers at once.
 - /rmblsticker <sticker link>: Same as above.

Note:
 - `<sticker link>` can be `https://t.me/addstickers/<sticker>` or just `<sticker>` or reply to the sticker message.
""",
	"supportcmd": """
*Currently support command*

*「 For Members 」*
*Admin*
-> `/adminlist` | `/admins`

*Anti Flood*
-> `/flood`

*Blacklist*
-> `/blacklist`

*Blacklist Sticker*
-> `/blsticker`

*Filter*
-> `/filters`

*Notes*
-> `/get`
-> `/notes` | `/saved`

*Rules*
-> `/rules`

*Warnings*
-> `/warns`
-> `/warnlist` | `/warnfilters`

*「 Admin Only 」*
*Admin*
-> `/adminlist`

*Anti Flood*
-> `/setflood`
-> `/flood`

*Backups*
-> `/import`
-> `/export`

*Banned*
-> `/ban`
-> `/tban` | `/tempban`
-> `/kick`
-> `/unban`

*Blacklist*
-> `/blacklist`
-> `/addblacklist`
-> `/unblacklist` | `/rmblacklist`

*Blacklist Sticker*
-> `/blsticker`
-> `/addblsticker`
-> `/unblsticker` | `/rmblsticker`

*Disabler*
-> `/enable`
-> `/disable`
-> `/cmds`

*Filter*
-> `/filter`
-> `/stop`
-> `/filters`

*Locks*
-> `/lock`
-> `/unlock`
-> `/locks`

*Notes*
-> `/get`
-> `/save`
-> `/clear`
-> `/notes` | `/saved`

*Mute user*
-> `/mute`
-> `/unmute`
-> `/tmute`

*Rules*
-> `/rules`
-> `/setrules`
-> `/clearrules`

*Warns*
-> `/warn`
-> `/resetwarn` | `/resetwarns`
-> `/warns`
-> `/addwarn`
-> `/nowarn` | `/stopwarn`
-> `/warnlist` | `/warnfilters`
-> `/warnlimit`
-> `/warnmode`
""",
	"connection_help": """
Organize your group via PM easily.

 - /connect <chatid/tag>: Connect to remote chat
 - /connection: Request a list of supported command commands
 - /disconnect: Disconnect from chat
 - /allowconnect on/yes/off/no: Allow connecting non-admin users to groups
 - /helpconnect: Get command help for connections
""",
	"filters_help": """
 - /filters: list all active filters in this chat.

*Admin only:*
 - /filter <keyword> <reply message>: add a filter to this chat. The bot will now reply that message whenever 'keyword' is mentioned. If you reply to a sticker with a keyword, the bot will reply with that sticker. 
NOTE: all filter keywords are in lowercase. If you want your keyword to be a sentence, use quotes. eg: /filter "hey there" How you doin?
 - /stop <filter keyword>: stop that filter.
""",
	"disable_help": """
 - /cmds: check the current status of disabled commands

*Admin only:*
 - /enable <cmd name>: enable that command
 - /disable <cmd name>: disable that command
 - /listcmds: list all possible toggleable commands
 - /disabledel: delete message when command is disabled
    """,
    "feds_help": """
Ah, group management. It's all fun and games, until you start getting spammers in, and you need to ban them. Then you need to start banning more, and more, and it gets painful.
But then you have multiple groups, and you don't want these spammers in any of your groups - how can you deal? Do you have to ban them manually, in all your groups?

No more! With federations, you can make a ban in one chat overlap to all your other chats.
You can even appoint federation admins, so that your trustworthiest admins can ban across all the chats that you want to protect.

*Commands:*
 - /fedstat: List all the federations you've been banned from.
 - /fedstat <user ID>: Lists all the federations the specified user has been banned from (also works with username, mention, and replies).
 - /fedstat <user ID> <Fed ID>: Gives information on the specified user's ban reason in that federation. If no user is specified, checks the sender.
 - /joinfed <FedID>: Joins the current chat to the federation. Each chat can only be in one federation. Only chat owners can do this.
 - /leavefed <FedID>: Leaves the current federation. Only chat owners can do this.

*Only federation admin:*
 - /newfed <fedname>: Creates a new federation with the given name. Users are only allowed to own one federation. Using this method when you already have a fed will simply change the federation name. (max 64 characters)
 - /delfed: Deletes your federation, and any information relating to it. Will not unban any banned users.
 - /fedinfo <FedID>: Information about the specified federation.
 - /fbroadcast <teks>: Broadcast text to all groups that join the federation.
 - /fban <user>: Bans a user from the current chat's federation.
 - /unfban <user>: Unbans a user the current chat's federation.
 - /setfrules: Set federation rules.
 - /frules: See federation regulations.
 - /chatfed: See current federation.
 - /fedadmins: Show federated admin.
 - /fednotif <on/off>: Set federation notified in PM when user is fban/unfban.
 - /fedchats: Get all chat connected in federation.

*Only federation owner:*
 - /fpromote <user>: Promotes the user to fed admin in your fed.
 - /fdemote <user>: Demotes the user from fed admin to normal user, in your fed.
 - /fbanlist: Get the list of currently banned users. If you want different modes, use /fbanlist <csv/json>
 - /importfbans: Reply federated backup message file to import banned list to current federation.
 - /subfed <fedid>: to subscribe federation, can subscribe multiple federations.
 - /unsubfed <fedid>: unsubscribe that federation.
 - /fedsubs: check all subscribed in current federation.
 - /myfeds: Get all your feds, only for feds owner.
""",
    "globalbans_help": """
*Admin only:*
 - /gbanstat <on/off/yes/no>: Will disable the effect of global bans on your group, or return your current settings.

Gbans, also known as global bans, are used by the bot owners to ban spammers across all groups. This helps protect \
you and your groups by removing spam flooders as quickly as possible. They can be disabled for you group by calling \
/gbanstat
""",
	"locks_help": """
 - /locktypes: a list of possible locktypes

*Admin only:*
 - /lock <type>: lock items of a certain type (not available in private)
 - /unlock <type>: unlock items of a certain type (not available in private)
 - /locks: the current list of locks in this chat.
 - /lockwarns <on/off/yes/no>: whether or not warn users sending locked messages.

Locks can be used to restrict a group's users.
eg:
Locking urls will auto-delete all messages with urls, locking stickers will delete all \
stickers, etc.
Locking bots will stop non-admins from adding bots to the chat.

*Note:*
 - Unlocking permission *info* will allow members (non-admins) to change the group information, such as the description or the group name
 - Unlocking permission *pin* will allow members (non-admins) to pinned a message in a group
""",
	"logchannel_help": """
*Admin only:*
- /logchannel: get log channel info
- /setlog: set the log channel.
- /unsetlog: unset the log channel.

Setting the log channel is done by:
- adding the bot to the desired channel (as an admin!)
- sending /setlog in the channel
- forwarding the /setlog to the group
""",
	"MARKDOWN_HELP": """
Markdown is a very powerful formatting tool supported by telegram. {} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.
- <code>_italic_</code>: wrapping text with '_' will produce italic text
- <code>*bold*</code>: wrapping text with '*' will produce bold text
- <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
- <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
EG: <code>[test](example.com)</code>
- <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
EG: <code>[This is a button](buttonurl:example.com)</code>
If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl:example.com)
[two](buttonurl:google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.
Keep in mind that your message <b>MUST</b> contain some text other than just a button!
""",
	"misc_help": """
 - /id: get the current group id. If used by replying to a message, gets that user's id.
 - /runs: reply a random string from an array of replies.
 - /slap: slap a user, or get slapped if not a reply.
 - /info: get information about a user.
 - /ping: check bot speed
 - /paste: Create a paste or a shortened url using [dogbin](https://del.dog)
 - /getpaste: Get the content of a paste or shortened url from [dogbin](https://del.dog)
 - /pastestats: Get stats of a paste or shortened url from [dogbin](https://del.dog)
 
 - /markdownhelp: quick summary of how markdown works in telegram - can only be called in private chats.
""",
   	"msgdel_help": """
*Admin only:*
 - /del: deletes the message you replied to
 - /purge: deletes all messages between this and the replied to message.
 - /purge <integer X>: deletes the replied message, and X messages following it.
""",
	"mute_help": """
*Admin only:*
 - /mute <userhandle>: silences a user. Can also be used as a reply, muting the replied to user.
 - /tmute <userhandle> x(m/h/d): mutes a user for x time. (via handle, or reply). m = minutes, h = hours, d = days.
 - /unmute <userhandle>: unmutes a user. Can also be used as a reply, muting the replied to user.
""",
	"notes_help": """
 - /get <notename>: get the note with this notename
 - #<notename>: same as /get
 - /notes or /saved: list all saved notes in this chat

If you would like to retrieve the contents of a note without any formatting, use `/get <notename> noformat`. This can \
be useful when updating a current note.

*Admin only:*
 - /save <notename> <notedata>: saves notedata as a note with name notename
A button can be added to a note by using standard markdown link syntax - the link should just be prepended with a \
`buttonurl:` section, as such: `[somelink](buttonurl:example.com)`. Check /markdownhelp for more info.
 - /save <notename>: save the replied message as a note with name notename
 - /clear <notename>: clear note with this name
  - /privatenote <on/yes/off/no> <? del>: whether or not to send the note in PM. Write `del` besides on/off to delete hashtag message on group.
""",
	"reporting_help": """
 - /report <reason>: reply to a message to report it to admins.
 - @admin: reply to a message to report it to admins.
NOTE: neither of these will get triggered if used by admins

*Admin only:*
 - /reports <on/off>: change report setting, or view current status.
   - If done in pm, toggles your status.
   - If in chat, toggles that chat's status.
""",
	"rss_help": """
 - /addrss <link>: add an RSS link to the subscriptions.
 - /removerss <link>: removes the RSS link from the subscriptions.
 - /rss <link>: shows the link's data and the last entry, for testing purposes.
 - /listrss: shows the list of rss feeds that the chat is currently subscribed to.

NOTE: In groups, only admins can add/remove RSS links to the group's subscription
""",
	"rules_help": """
 - /rules: get the rules for this chat.

*Admin only:*
 - /setrules <your rules here>: set the rules for this chat.
 - /clearrules: clear the rules for this chat.
 - /privaterules <yes/no/on/off>: should the rules be sent to private chat. Default: yes.
""",
	"userinfo_help": """
 - /setbio <text>: while replying, will save another user's bio
 - /bio: will get your or another user's bio. This cannot be set by yourself.
 - /setme <text>: will set your info
 - /me: will get your or another user's info
""",

#stickers	
	"stickers_help": """	
- /stickerid: reply to a sticker to me to tell you its file ID.
- /getsticker: reply to a sticker to me to upload its raw PNG file.
- /kang: reply to a sticker to add it to your pack.
""",
	
# warns
	"CURRENT_WARNING_FILTER_STRING": "<b>Current warning filters in this chat:</b>\n",
	"warns_help": """
 - /warns <userhandle>: get a user's number, and reason, of warnings.
 - /warnlist: list of all current warning filters

*Admin only:*
 - /warn <userhandle>: warn a user. After 3 warns, the user will be banned from the group. Can also be used as a reply.
 - /resetwarn <userhandle>: reset the warnings for a user. Can also be used as a reply.
 - /addwarn <keyword> <reply message>: set a warning filter on a certain keyword. If you want your keyword to \
be a sentence, encompass it with quotes, as such: `/addwarn "very angry" This is an angry user`. 
 - /nowarn <keyword>: stop a warning filter
 - /warnlimit <num>: set the warning limit
 - /warnmode <kick/ban/mute>: Set warn mode, when user exceeding the warn limit will result in that mode.
""",
	"weather_lang": "en",
	"weather_help": """
 - /weather <location>: get weather info in certain places
""",
	"WELC_HELP_TXT": "Your group's welcome/goodbye messages can be personalised in multiple ways. If you want the messages to be individually generated, like the default welcome message is, you can use *these* variables:\n - `{{first}}`: this represents the user's *first* name\n - `{{last}}`: this represents the user's *last* name. Defaults to *first name* if user has no last name.\n - `{{fullname}}`: this represents the user's *full* name. Defaults to *first name* if user has no last name.\n - `{{username}}`: this represents the user's *username*. Defaults to a *mention* of the user's first name if has no username.\n - `{{mention}}`: this simply *mentions* a user - tagging them with their first name.\n - `{{id}}`: this represents the user's *id*\n - `{{count}}`: this represents the user's *member number*.\n - `{{chatname}}`: this represents the *current chat name*.\n\nEach variable MUST be surrounded by `{{}}` to be replaced.\nWelcome messages also support markdown, so you can make any elements bold/italic/code/links. Buttons are also supported, so you can make your welcomes look awesome with some nice intro buttons.\nTo create a button linking to your rules, use this: `[Rules](buttonurl:{{rules}})`.\nIf you're feeling fun, you can even set images/gifs/videos/voice messages as the welcome message by replying to the desired media, and calling /setwelcome.",
    "welcome_help": """
*Admin only:*
 - /welcome <on/off>: enable/disable the welcome message.
 - /goodbye <on/off>: enable/disable goodbye message.
 - /welcome: show current welcome settings, without formatting - useful for recycling your welcome message!
 - /goodbye: same use and args as /welcome.
 - /setwelcome <sometext>: set a custom welcome message. If used to reply to media, use that media.
 - /setgoodbye <sometext>: set a custom goodbye message. If used to reply to media, use that media.
 - /resetwelcome: reset to the default welcome message.
 - /resetgoodbye: reset to the default goodbye message.
 - /cleanwelcome <on/off>: deletes old welcome messages; when a new person joins, the old message is deleted.
 - /cleanservice <on/off/yes/no>: deletes all service message; those are the annoying "x joined the group" you see when people join.
 - /welcomemute <on/ya/off/ga>: all users that join, get muted; a button gets added to the welcome message for them to unmute themselves. This proves they aren't a bot!
 - /welcomemutetime <Xw/d/h/m>: if a user hasnt pressed the "unmute" button in the welcome message after a certain this time, they'll get unmuted automatically after this period of time.
 Note: if you want to reset the mute time to be forever, use /welcomemutetime 0m. 0 == eternal!
 - /setmutetext <new text>: Customise the "Click here to unmute" button obtained from enabling welcomemutes.
 - /resetmutetext: Reset teks tombol unmute menjadi default.

 - /welcomeverify <on/off>: Enable welcome verification with images and buttons, best for anti bots
 - /wtimeout <Xw/d/h/m>: Set welcome timeout, when user wasn't verify for X, then that user will be kicked/banned
 - /wtmode <kick/ban>: Set welcome timeout should be kicked or banned

Read /welcomehelp and /markdownhelp to learn about formatting your text and mentioning new users when the join!

If you want to save an image, gif, or sticker, or any other data, do the following:
/setwelcome while replying to a sticker or whatever data you'd like. This data will now be sent to welcome new users.

Tip: use /welcome noformat to retrieve the unformatted welcome message.
This will retrieve the welcome message and send it without formatting it; getting you the raw markdown, allowing you to make easy edits.
This also works with /goodbye.
""",
	"cleaner_help": """
*Admin only:*
 - /cleanbluetext <on/off>: Delete all blue text message.

Note:
- This feature may broke others bot
""",
	"exclusive_help": """
 - /ping: check the speed of the bot
 - /fortune: give a fortune
 - /tr <from>-<to> <text>: translate text written or reply for any language to the intended language, or
 - /tr <to> <text>: translate text written or reply for any language to the intended language
 - /wiki <text>: search for text written from the wikipedia source
 - /ud <text>: search from urban dictionary
 - /thonkify <reply>/<args>: turns text into thonk text (only supports letters and none symbols for now).
 *Special | COVID-19*
 - /covid: Powered by Worldometers, Give stats about overall stats of COVID-19.
 - /covid <country name>: Powered by Worldometers, Give stats about COVID-19.

"""
}



RUN_STRINGS = (
    "Where do you think you're going?",
    "Huh? what? did they get away?",
    "ZZzzZZzz... Huh? what? oh, just them again, nevermind.",
    "Get back here!",
    "Not so fast...",
    "Look out for the wall!",
    "Don't leave me alone with them!!",
    "You run, you die.",
    "Jokes on you, I'm everywhere",
    "You're gonna regret that...",
    "You could also try /kickme, I hear that's fun.",
    "Go bother someone else, no-one here cares.",
    "You can run, but you can't hide.",
    "Is that all you've got?",
    "I'm behind you...",
    "You've got company!",
    "We can do this the easy way, or the hard way.",
    "You just don't get it, do you?",
    "Yeah, you better run!",
    "Please, remind me how much I care?",
    "I'd run faster if I were you.",
    "That's definitely the droid we're looking for.",
    "May the odds be ever in your favour.",
    "Famous last words.",
    "And they disappeared forever, never to be seen again.",
    "\"Oh, look at me! I'm so cool, I can run from a bot!\" - this person",
    "Yeah yeah, just tap /kickme already.",
    "Here, take this ring and head to Mordor while you're at it.",
    "Legend has it, they're still running...",
    "Unlike Harry Potter, your parents can't protect you from me.",
    "Fear leads to anger. Anger leads to hate. Hate leads to suffering. If you keep running in fear, you might "
    "be the next Vader.",
    "Multiple calculations later, I have decided my interest in your shenanigans is exactly 0.",
    "Legend has it, they're still running.",
    "Keep it up, not sure we want you here anyway.",
    "You're a wiza- Oh. Wait. You're not Harry, keep moving.",
    "NO RUNNING IN THE HALLWAYS!",
    "Hasta la vista, baby.",
    "Who let the dogs out?",
    "It's funny, because no one cares.",
    "Ah, what a waste. I liked that one.",
    "Frankly, my dear, I don't give a damn.",
    "My milkshake brings all the boys to yard... So run faster!",
    "You can't HANDLE the truth!",
    "A long time ago, in a galaxy far far away... Someone would've cared about that. Not anymore though.",
    "Hey, look at them! They're running from the inevitable banhammer... Cute.",
    "Han shot first. So will I.",
    "What are you running after, a white rabbit?",
    "As The Doctor would say... RUN!",
)

SLAP_TEMPLATES = (
    "{user1} {hits} {user2} with a {item}.",
    "{user1} {hits} {user2} in the face with a {item}.",
    "{user1} {hits} {user2} around a bit with a {item}.",
    "{user1} {throws} a {item} at {user2}.",
    "{user1} grabs a {item} and {throws} it at {user2}'s face.",
    "{user1} launches a {item} in {user2}'s general direction.",
    "{user1} starts slapping {user2} silly with a {item}.",
    "{user1} pins {user2} down and repeatedly {hits} them with a {item}.",
    "{user1} grabs up a {item} and {hits} {user2} with it.",
    "{user1} ties {user2} to a chair and {throws} a {item} at them.",
    "{user1} gave a friendly push to help {user2} learn to swim in lava."
)

ITEMS = (
    "cast iron skillet",
    "large trout",
    "baseball bat",
    "cricket bat",
    "wooden cane",
    "nail",
    "printer",
    "shovel",
    "CRT monitor",
    "physics textbook",
    "toaster",
    "portrait of Richard Stallman",
    "television",
    "five ton truck",
    "roll of duct tape",
    "book",
    "laptop",
    "old television",
    "sack of rocks",
    "rainbow trout",
    "rubber chicken",
    "spiked bat",
    "fire extinguisher",
    "heavy rock",
    "chunk of dirt",
    "beehive",
    "piece of rotten meat",
    "bear",
    "ton of bricks",
)

THROW = (
    "throws",
    "flings",
    "chucks",
    "hurls",
)

HIT = (
    "hits",
    "whacks",
    "slaps",
    "smacks",
    "bashes",
)


RAMALAN_STRINGS = (
	"There’s a friend who would be happy to hear from you today\nTell them I said “Hi”",
	"5 - 8 - 27 - 38 - 42 - 48\nWhoops! That was the back!",
	"You're due for a good documentary",
	"It's a good time to re-read your favorite book",
	"Consider adding a little extra color to your wardrobe tomorrow 👠",
	"Make sure you drink enough water today\nThat’s not so much a fortune as a general guideline to keep feeling alright",
	"A stranger will come into your life with a BANG 💥",
	"It's great to be grateful\nThank somebody today",
	"Temptation is often disguised as opportunity",
	"Now is the right time to do something you've put off",
	"You can't get what you don't ask for 👐",
	"Never let a cookie tell you what to do",
	"Trust decisions where your emotions and logic agree",
	"Animal companionship can bring a smile to even the most frowny face ️😔 🐶 😊",
	"If you make someone’s day, your day will be made, too\nIt pretty much always works that way 😊",
	"Knowing that an illusion isn’t real doesn’t it make it less magical",
	"The next meal you cook will be your best yet 🍴",
	"You'll notice something new in your neighborhood soon 🏡",
	"Today will be yesterday tomorrow",
	"Indulge in some nostalgia; sweet memories can be good medicine",
	"Today is a good day to listen to your intuition rather than advice 🚶",
	"It's a good day to appreciate the little things",
	"Embrace your goals\nSmooch your dreams 😘 🌙",
	"That food you've never tasted might actually taste good",
	"Hear no evil 🙉, see no evil 🙈, tweet no evil 🐥",
	"You will learn a new dance\nAnd you'll be really good at it",
	"Try going somewhere new, even if it's just a few miles away from home",
	"Do something you love today 💞\nI can all but promise happiness awaits 😀",
	"It's time to try out a new hobby",
	"An opportunity will present itself if you pay attention 👀",
	"Companionship is right within your reach\nIn fact, you're holding it right now 😊",
	"Keep doing what you’re doing and it will be done\nOk, even I will admit that was a weak fortune",
	"In life, there is but one truth\nHe who smelt it, delt it",
	"If you listen closely, the wind will provide all of lifes answers 💨",
	"Positive things will enter your life today\nBut bear in mind that most of them will be atomically bonded to negative things 🔬😀",
	"A great gift awaits\nBut fair warning, it’s a very patient gift",
	"It's a good time for a new creative pursuit",
	"Stop and smell the roses\nReally, any flowers you come across willl do 💐",
	"You will pick up a good book tonight\nBut ultimately decide to free the spider outside",
	"You're about to receive a new message from your Google Assistant:\nHI 😀",
	"Make a playlist for a friend this week 🎧",
	"Your favorite YouTube video is yet to be found",
	"Take some time to listen to your loved ones",
	"Make sure to laugh at something silly today 😆",
	"The one you love is closer than you think 💞",
	"You're going to hear a song that will make you smile for days",
	"Keep your head up, because good things are coming your way 😎",
	"When in doubt, Google it 😉",
	"May you go from strength to strength",
	"Error 404: Fortune not found\nTry again soon 😉",
	"The next time you go out to eat, you will order dessert\nNot exactly a fortune, more like a good idea 🍪",
	"Chase the dawn and your shadow will be behind you",
	"You are admired for your talents more than you realize 👏",
	"It's a good time to learn a new skill",
	"Fortune favors the bold\nLuck favors the italic",
	"It's the right time to act like the person you want to be",
	"Pay attention to the details\nYou might notice something interesting",
	"An unexpected visitor will surprise you with a treat",
	"Walk a block out of your way today",
	"A new adventure lurks right around the corner",
	"You will get a taste of something unexpected",
	"Go somewhere you've never been, and see what you find there",
	"Seek not fortunes in the inedible",
	"It's a great time to plan a trip with someone you love ✈️",
	"Send an old friend a message today",
	"Trust your instincts\nWin that bear 🎯🐻",
	"Someone will invite you to a karaoke party 🎶",
	"An exciting email is coming your way soon"
)

RAMALAN_FIRST = (
	"I've got a fortune for you.\n",
	"I'm no cookie, but I do know some fortunes.\n",
	"One fortune, coming right up.\n"
)
