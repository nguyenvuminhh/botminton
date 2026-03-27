# Bot Commands

## Group chat

### Poll
| Command | Description |
|---|---|
| `/open_poll` | Send a YES/NO poll to the group for the next session. Auto-closes Thursday midnight. |
| `/close_poll` | Manually close the current poll early |

### Session management (admin)
Use `@username` for players who have one, or their first name for those who don't.

| Command | Args | Description |
|---|---|---|
| `/add_player` | `<name>` | Manually add a player to the current session |
| `/remove_player` | `<name>` | Remove a player from the current session |
| `/add_plus_one` | `<name>` | Add a +1 for a player |
| `/remove_plus_one` | `<name>` | Remove a +1 from a player |
| `/set_slots` | `<number>` | Log the number of slots played (e.g. `6.0` = 3 courts × 2 hrs) |
| `/set_venue` | `<name>` | Set the venue for the current session |

### Period management (admin)
| Command | Args | Description |
|---|---|---|
| `/end_current_and_start_new_period` | `[YYYY-MM-DD]` | Post period summary to group, close current period, start a new one. Defaults to today. |
| `/period_summary` | — | Calculate and post the money summary for the current period |
| `/add_shuttlecock` | `<price1> [price2] ...` | Log tube prices to the current period — one arg per tube (e.g. `/add_shuttlecock 11.4 11.4 12.0`) |

### Venue management (admin)
| Command | Args | Description |
|---|---|---|
| `/list_venues` | — | List all registered venues with price per slot |
| `/add_venue` | `<price> <location> <name>` | Register a new venue (e.g. `/add_venue 10.0 Unisport Unisport student`) |

---

## Private chat (admin only)

| Command | Args | Description |
|---|---|---|
| `/print_user_id` | — | Print your Telegram user ID and admin status |
| `/print_group_chat_id` | — | Print the group chat ID |
| `/test_admin` | — | Verify admin access |
| `/payment_status` | — | Show numbered paid/unpaid list for the most recently closed period |
| `/mark_paid` | `1 3 5 ...` | Preview players to mark as paid (by index from `/payment_status`), ask for confirmation |
| `/confirm_paid` | — | Confirm the pending `/mark_paid` action |
