import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
COMMON_GROUP_CHAT_ID = os.environ["COMMON_GROUP_CHAT_ID"]
ADMIN_USER_ID = os.environ["ADMIN_USER_ID"]
ADMIN_USER_IDS = [ADMIN_USER_ID]