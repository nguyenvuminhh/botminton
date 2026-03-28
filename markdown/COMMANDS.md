# Bot Commands

## Group chat

### Poll
| Command | Description |
|---|---|
| `/openpoll` | Send a YES/NO poll to the group for the next session. Auto-closes Thursday midnight. |
| `/closepoll` | Manually close the current poll early |

### Session management (admin)
Use `@username` for players who have one, or their first name for those who don't.

| Command | Args | Description |
|---|---|---|
| `/addplayer` | `<name>` | Manually add a player to the current session |
| `/removeplayer` | `<name>` | Remove a player from the current session |
| `/addplusone` | `<name>` | Add a +1 for a player |
| `/removeplusone` | `<name>` | Remove a +1 from a player |
| `/setslots` | `<number>` | Log the number of slots played (e.g. `6.0` = 3 courts × 2 hrs) |
| `/setvenue` | `<name>` | Set the venue for the current session |

### Period management (admin)
| Command | Args | Description |
|---|---|---|
| `/endcurrentandstartnewperiod` | `[YYYY-MM-DD]` | Post period summary to group, close current period, start a new one. Defaults to today. |
| `/periodsummary` | — | Calculate and post the money summary for the current period |
| `/addshuttlecock` | `<price1> [price2] ...` | Log tube prices to the current period — one arg per tube (e.g. `/addshuttlecock 11.4 11.4 12.0`) |

### Venue management (admin)
| Command | Args | Description |
|---|---|---|
| `/listvenues` | — | List all registered venues with price per slot |
| `/addvenue` | `<price> <location> <name>` | Register a new venue (e.g. `/addvenue 10.0 Unisport Unisport student`) |
| `/setschedule` | `<start> <end> [day]` | Set default session time and day (e.g. `/setschedule 20:30 22:00 fri`). Day accepts `mon`–`sun`, full name, or index (0=Mon). Run with no args to view current schedule. |

---

## Private chat (admin only)

| Command | Args | Description |
|---|---|---|
| `/printuserid` | — | Print your Telegram user ID and admin status |
| `/printgroupchatid` | — | Print the group chat ID |
| `/testadmin` | — | Verify admin access |
| `/paymentstatus` | — | Show numbered paid/unpaid list for the most recently closed period |
| `/markpaid` | `1 3 5 ...` | Preview players to mark as paid (by index from `/paymentstatus`), ask for confirmation |
| `/confirmpaid` | — | Confirm the pending `/markpaid` action |
