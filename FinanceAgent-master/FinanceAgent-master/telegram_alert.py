import logging
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_CHAT_ID = os.environ.get('CHATID',  None)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', None)

def send_message(text):
    import requests
    bot_token = TELEGRAM_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    message = text
   
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message
    }
   
    response = requests.post(url, data=params)

# class TelegramLogHandler(logging.Handler):
#     def init(self, chat_id: str):
#         super().init()
#         self.chat_id = chat_id

#     def emit(self, record):
#         try:
#             log_message = self.format(record)

#             send_message(log_message)
#         except Exception as e:
#             logging.error(f"Failed to send message to Telegram: {e}")


# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(name)

# telegram_handler = TelegramLogHandler(chat_id=TELEGRAM_CHAT_ID)
# telegram_handler.setLevel(logging.INFO)
# telegram_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
# logger.addHandler(telegram_handler)
