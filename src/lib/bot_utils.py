import logging
import os

from telegram import Update, Bot

logger = logging.getLogger(os.path.basename(__file__))


class BotUtils:
    def __init__(self, config, auth_chat_ids, bot: Bot):
        # Constructor
        self.config = config
        self.auth_chat_ids = auth_chat_ids
        self.bot = bot

    @staticmethod
    def check_last_and_delete(_, context, message):
        if "last_message" in context.user_data and message is not None:
            context.user_data["last_message"].delete()
            context.user_data["last_message"] = message
        elif "last_message" in context.user_data and message is None:
            context.user_data["last_message"].delete()
            del context.user_data["last_message"]
        elif "last_message" not in context.user_data and message is not None:
            context.user_data["last_message"] = message
        else:
            pass  # message not present or not passed

    def is_admin(self, username):
        return username == self.config["admin"]

    def log_admin(self, msg, update: Update, context):
        if not self.is_admin(update.effective_user.username):
            for k1, v1 in self.auth_chat_ids.items():
                if v1["username"] == self.config["users"]["admin"]:
                    context.bot.send_message(k1, text=msg)

    def check_admin_logged(self) -> bool:
        for k1, v1 in self.auth_chat_ids.items():
            return v1["active"] is True and v1["admin"] is True

    def is_allowed(self, username) -> bool:
        return username in self.config["users"]
