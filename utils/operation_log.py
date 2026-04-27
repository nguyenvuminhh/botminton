import logging
from datetime import datetime, timezone
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from config import OPERATION_LOG_GROUP_CHAT_ID

logger = logging.getLogger(__name__)

# (human-readable description, first arg is "to whom")
_COMMAND_META: dict[str, tuple[str, bool]] = {
    "addplayer":                   ("Added player",                True),
    "removeplayer":                ("Removed player",              True),
    "addplusone":                  ("Added plus-one",              True),
    "removeplusone":               ("Removed plus-one",            True),
    "setslots":                    ("Set session slots",           False),
    "setvenue":                    ("Set session venue",           False),
    "openpoll":                    ("Opened poll",                 False),
    "closepoll":                   ("Closed poll",                 False),
    "addshuttlecock":              ("Added shuttlecock batch",     False),
    "periodsummary":               ("Requested period summary",    False),
    "endcurrentandstartnewperiod": ("Ended period & started new", False),
    "addvenue":                    ("Added venue",                 False),
    "listvenues":                  ("Listed venues",               False),
    "setschedule":                 ("Set schedule",                False),
    "paymentstatus":               ("Checked payment status",      False),
    "markpaid":                    ("Staged players as paid",      False),
    "confirmpaid":                 ("Confirmed payment",           False),
    "testadmin":                   ("Tested admin status",         False),
    "printgroupchatid":            ("Printed group chat ID",       False),
    "printuserid":                 ("Printed user ID",             False),
}


def _format_user(full_name: str, username: str | None, telegram_id: str | int) -> str:
    if username:
        return f"{full_name} (@{username}) · {telegram_id}"
    return f"{full_name} · {telegram_id}"


async def send_operation_log(
    bot,
    actor_first_name: str,
    actor_last_name: str | None,
    actor_username: str | None,
    actor_id: int,
    did_what: str,
    target_username_arg: str | None = None,
    extra_info: str | None = None,
) -> None:
    if not OPERATION_LOG_GROUP_CHAT_ID:
        return

    now = datetime.now(tz=timezone.utc)
    timestamp = now.strftime("%d/%m/%Y %H:%M UTC")

    actor_full = actor_first_name
    if actor_last_name:
        actor_full += f" {actor_last_name}"

    lines = [
        f"- Datetime: {timestamp}",
        f"- Who did: {_format_user(actor_full, actor_username, actor_id)}",
        f"- Did what: {did_what}",
    ]

    if target_username_arg:
        from services.users import get_user_by_username
        raw = target_username_arg.lstrip("@")
        target = get_user_by_username(raw)
        if target:
            lines.append(
                f"- To whom: {_format_user(str(target.full_name), str(target.telegram_user_name) if target.telegram_user_name else None, str(target.telegram_id))}"
            )
        else:
            lines.append(f"- To whom: @{raw} (unregistered)")

    if extra_info:
        lines.append(f"- Extra info: {extra_info}")

    try:
        await bot.send_message(chat_id=OPERATION_LOG_GROUP_CHAT_ID, text="\n".join(lines))
    except Exception as exc:
        logger.warning("Failed to send operation log: %s", exc)


def operation_log_middleware(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = await func(update, context)

        user = update.effective_user
        if not user or not update.message or not update.message.text:
            return result

        raw_cmd = update.message.text.split()[0].lstrip("/").lower()
        if "@" in raw_cmd:
            raw_cmd = raw_cmd.split("@")[0]

        description, has_target = _COMMAND_META.get(raw_cmd, (f"/{raw_cmd}", False))
        args = list(context.args or [])

        target_arg = args[0] if has_target and args else None
        extra_args = args[1:] if has_target and args else args
        extra_info = " ".join(extra_args) if extra_args else None

        await send_operation_log(
            bot=context.bot,
            actor_first_name=user.first_name,
            actor_last_name=user.last_name,
            actor_username=user.username,
            actor_id=user.id,
            did_what=description,
            target_username_arg=target_arg,
            extra_info=extra_info,
        )
        return result

    return wrapper
