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
                if v1["username"] == self.config["admin"]:
                    context.bot.send_message(k1, text=msg)

    def is_admin_logged(self) -> bool:
        for k1, v1 in self.auth_chat_ids.items():
            if v1["active"] is True and v1["admin"] is True:
                return True
        return False

    def is_allowed(self, username) -> bool:
        for user, _ in self.config["users"].items():
            if user == username:
                return True

    def init_user(self, chat_id, username):
        if chat_id not in self.auth_chat_ids:
            self.auth_chat_ids[chat_id] = dict()
            self.auth_chat_ids[chat_id]["username"] = username
            self.auth_chat_ids[chat_id]["active"] = True
            self.auth_chat_ids[chat_id]["admin"] = self.is_admin(username)
            self.auth_chat_ids[chat_id]["cameras"] = self.config["users"][username]["cameras"]
            self.auth_chat_ids[chat_id]["switches"] = self.config["users"][username]["switches"]

    def get_logged_users(self):
        return dict((k, v) for k, v in self.auth_chat_ids.items() if v["active"] is True)

    def get_logged_and_auth_camera_users(self, camera: str):
        return dict((k, v) for k, v in self.auth_chat_ids.items() if v["active"] is True and camera in v["cameras"])

    def send_image_to_logged_auth_users(self, camera: str, image, caption: str, notification: bool = True):
        if self.is_admin_logged():
            logged_users = self.get_logged_and_auth_camera_users(camera)
            for chatId, value in logged_users.items():
                self.bot.send_photo(chat_id=chatId, photo=image, caption=caption, disable_notification=notification)

    def send_msg_to_logged_auth_users(self, camera: str, message: str, notification: bool = True):
        if self.is_admin_logged():
            logged_users = self.get_logged_and_auth_camera_users(camera)
            for chatId, value in logged_users.items():
                self.bot.send_message(chatId, text=message, disable_notification=notification)
