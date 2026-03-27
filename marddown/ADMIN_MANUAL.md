# ADMIN_MANUAL.md

This is the week-to-week operating guide for admins.

---

## Weekly routine

### 1. Open the poll (start of week)

```
/open_poll
```

Posts a YES/NO poll to the group for the next session. The poll auto-closes Thursday midnight UTC. Players vote to register their attendance.

---

### 2. After the session

**Set how many slots were played:**
```
/set_slots 6.0
```
Slots = courts × hours. Example: 3 courts × 2 hrs = `6.0`.

**Set the venue (if it changed):**
```
/set_venue Unisport student
```
The venue is remembered for future sessions — you only need this when it changes.

**Adjust the attendee list if needed:**
```
/add_player @username        # add someone who forgot to vote
/remove_player @username     # remove someone who didn't show
/add_plus_one @username      # player brought a guest
/remove_plus_one @username   # undo a plus-one
```

**Log shuttlecocks purchased:**
```
/add_shuttlecock 11.4 11.4 12.0
```
Each argument is the price of one tube. The bot sums them up automatically. The purchase is logged to the current period.

---

### 3. Close a period and collect money

When you're ready to collect (typically every 2–3 weeks):

```
/end_current_and_start_new_period
```

This does three things in one command:
1. Calculates the money summary and posts it to the group
2. Closes the current period
3. Starts a new period from today

> To post the summary without closing the period, use `/period_summary` instead.

---

### 4. Track payments (private chat)

Once the summary is posted, switch to your private chat with the bot.

**See who has paid:**
```
/payment_status
```
Shows a numbered list of all players and their payment status for the last closed period:
```
Period 01/01 → 01/03
1. alice — 12.50 ✅
2. bob — 11.00 ❌
3. charlie — 9.80 ❌
```

**Mark players as paid:**
```
/mark_paid 2 3
```
The bot shows a preview of who will be marked. Confirm with:
```
/confirm_paid
```

---

## Venue management

**List registered venues:**
```
/list_venues
```

**Add a new venue:**
```
/add_venue 10.0 Unisport "Unisport student"
```
Format: `/add_venue <price_per_slot> <location> <name>`

Price per slot is in EUR per court-hour. Example: 3 courts × 2 hrs at 10 €/slot = 60 € total.

---

## How costs are split

**Court costs** — per session, divided by weight:
- Each player's weight = `1 + number of plus-ones they brought`
- Player's share = `(session_total / total_weight) × player_weight`

**Shuttlecock costs** — across the whole period:
- Distributed proportionally by how many sessions each player attended (weighted)
- Players who attended more sessions pay more toward shuttlecocks

---

## Utility commands (private chat)

| Command | Description |
|---|---|
| `/print_user_id` | Your Telegram user ID and admin status |
| `/print_group_chat_id` | The group chat ID |
| `/test_admin` | Verify you have admin access |
