import logging
import os

from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update

from bot.conversation.fsm import bot_states, bot_events
from bot.utils.bot_utils import BotUtils

logger = logging.getLogger(os.path.basename(__file__))


class RootCommand(object):
    # Constructor
    def __init__(self, config, auth_chat_ids, conversation_utils: BotUtils):
        self.config = config
        self.auth_chat_ids = auth_chat_ids
        self.utils = conversation_utils

    # STATE=START
    def start(self, update: Update, context):
        chat_id = update.effective_chat.id
        user = update.effective_user
        # Store value
        text = "Welcome to *Home Control Bot* by *NiNi* [link](https://github.com/Giulianini/yi-hack-control-bot)\n"
        if not self.utils.is_allowed(user.username):
            text = text + "🚫 User not allowed 🚫"
            message = context.bot.send_message(chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)
            self.utils.check_last_and_delete(update, context, message)
            log_msg = "{} ({} {}) denied.".format(user.username, user.first_name, user.last_name)
            logger.warning(log_msg)
            self.utils.log_admin(log_msg, update, context)
            return bot_states.NOT_LOGGED
        # Init user if not exists
        self.utils.init_user(chat_id, user.username)
        log_msg = "{} ({} {}) active.".format(user.username, user.first_name, user.last_name)
        logger.warning(log_msg)
        self.utils.log_admin(log_msg, update, context)
        message = context.bot.send_message(chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        self.utils.check_last_and_delete(update, context, message)
        return bot_states.LOGGED

    def show_logged_menu(self, update, context):
        self.utils.check_last_and_delete(update, context, None)
        update.message.delete()
        keyboard = [[InlineKeyboardButton(text="Snapshot", callback_data=str(bot_events.SNAPSHOT_CLICK))],
                    [InlineKeyboardButton(text="Video", callback_data=str(bot_events.VIDEO_CLICK))],
                    [InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))]
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text="Menu", reply_markup=reply_markup)
        return bot_states.LOGGED

    @staticmethod
    def exit(update: Update, _):
        update.callback_query.answer()
        update.effective_message.delete()
        return bot_states.LOGGED
