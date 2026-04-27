import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
COMMON_GROUP_CHAT_ID = os.environ["COMMON_GROUP_CHAT_ID"]
ADMIN_USER_ID = os.environ["ADMIN_USER_ID"]
ADMIN_USER_IDS = [ADMIN_USER_ID]

WEBHOOK_URL    = os.environ.get("WEBHOOK_URL")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")
PUBLIC_BASE_URL = (os.environ.get("PUBLIC_BASE_URL") or WEBHOOK_URL or "").rstrip("/")

LOG_GROUP_CHAT_ID = os.environ.get("LOG_GROUP_CHAT_ID")
OPERATION_LOG_GROUP_CHAT_ID = os.environ.get("OPERATION_LOG_GROUP_CHAT_ID")

JWT_SECRET = os.environ["JWT_SECRET"]
API_PORT   = int(os.environ.get("API_PORT", "8000"))