import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
ADMIN_GROUP_CHAT_ID = os.environ["ADMIN_GROUP_CHAT_ID"]
COMMON_GROUP_CHAT_ID = os.environ["COMMON_GROUP_CHAT_ID"]
ADMIN_1_USER_ID = os.environ["ADMIN_1_USER_ID"]
ADMIN_2_USER_ID = os.environ["ADMIN_2_USER_ID"]
ADMIN_USER_IDS = [ADMIN_1_USER_ID, ADMIN_2_USER_ID]