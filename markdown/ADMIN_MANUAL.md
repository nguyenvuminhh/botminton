# ADMIN_MANUAL.md

This is the week-to-week operating guide for admins.

---

## Weekly routine

### 1. Open the poll (start of week)

```
/openpoll
```

Posts a YES/NO poll to the group for the next session. The poll auto-closes Thursday midnight UTC. Players vote to register their attendance.

---

### 2. After the session

**Set how many slots were played:**
```
/setslots 6.0
```
Slots = courts × hours. Example: 3 courts × 2 hrs = `6.0`.

**Set the venue (if it changed):**
```
/setvenue Unisport student
```
The venue is remembered for future sessions — you only need this when it changes.

**Adjust the attendee list if needed:**
```
/addplayer @username        # add someone who forgot to vote
/removeplayer @username     # remove someone who didn't show
/addplusone @username       # player brought a guest
/removeplusone @username    # undo a plus-one
```
For players without a `@username`, use their first name instead (e.g. `/addplayer Minh`).

**Log shuttlecocks purchased:**
```
/addshuttlecock 11.4 11.4 12.0
```
Each argument is the price of one tube. The bot sums them up automatically. The purchase is logged to the current period.

---

### 3. Close a period and collect money

When you're ready to collect (typically every 2–3 weeks):

```
/endcurrentandstartnewperiod
```

This does three things in one command:
1. Calculates the money summary and posts it to the group
2. Closes the current period
3. Starts a new period from today

> To post the summary without closing the period, use `/periodsummary` instead.

---

### 4. Track payments (private chat)

Once the summary is posted, switch to your private chat with the bot.

**See who has paid:**
```
/paymentstatus
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
/markpaid 2 3
```
The bot shows a preview of who will be marked. Confirm with:
```
/confirmpaid
```

---

## Venue management

**List registered venues:**
```
/listvenues
```

**Add a new venue:**
```
/addvenue 10.0 Unisport "Unisport student"
```
Format: `/addvenue <price_per_slot> <location> <name>`

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
| `/printuserid` | Your Telegram user ID and admin status |
| `/printgroupchatid` | The group chat ID |
| `/testadmin` | Verify you have admin access |
