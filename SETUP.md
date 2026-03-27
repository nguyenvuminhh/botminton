# SETUP.md

## Prerequisites

- Python 3.11+
- A MongoDB database (MongoDB Atlas free tier works)
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))
- Two Telegram groups: one for the main players, one for admin use

---

## 1. Create the Telegram bot

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → follow the prompts
2. Copy the **bot token**
3. Disable the bot's privacy mode so it can read group messages:
   BotFather → `/mybots` → select your bot → **Bot Settings** → **Group Privacy** → **Turn off**

---

## 2. Get Telegram IDs

Add the bot to the group, then message it in private:

- `/print_user_id` — your Telegram user ID (needed for `ADMIN_USER_ID`)
- `/print_group_chat_id` — run this inside the group to get its chat ID

> The group chat ID is typically a negative number like `-1001234567890`.

---

## 3. Configure environment

Copy `example.env` to `.env` and fill in all values:

```
BOT_TOKEN=              # From BotFather
MONGODB_URI=            # e.g. mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=          # e.g. botminton
COMMON_GROUP_CHAT_ID=   # The group chat ID (negative number)
ADMIN_USER_ID=          # Your Telegram user ID
```

---

## 4. Install dependencies and run

```bash
pip install -r requirements.txt
python -m botminton
```

---

## 5. First-time setup (run once)

After the bot is running, do these steps in order:

**a) Register a venue**
In the group chat:
```
/add_venue 10.0 Unisport "Unisport student"
```
Format: `/add_venue <price_per_slot> <location> <name>`

**b) Start the first billing period**
```
/end_current_and_start_new_period
```
This starts a new period from today. You'll run this again at the end of each billing cycle.

**c) Open the first poll**
```
/open_poll
```
The bot sends a YES/NO poll to the group. It auto-closes Thursday midnight UTC.

The bot is now ready to use.
