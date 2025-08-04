# Botminton Services Documentation

This document provides comprehensive documentation for all services in the Botminton application. These services provide CRUD operations and business logic for managing users, sessions, periods, and related data.

## Table of Contents

1. [UserService](#userservice)
2. [SessionService](#sessionservice)
3. [PeriodService](#periodservice)
4. [PeriodMoneyService](#periodmoneyservice)
5. [SessionParticipantService](#sessionparticipantservice)
6. [Usage Examples](#usage-examples)
7. [Error Handling](#error-handling)

---

## UserService

Manages user data and operations.

### Class Methods

#### `create_user(telegram_id: str, telegram_user_name: Optional[str] = None) -> Optional[Users]`

Creates a new user or returns existing user if telegram_id already exists.

**Parameters:**
- `telegram_id` (str): Unique Telegram user ID
- `telegram_user_name` (Optional[str]): Telegram username (default: None)

**Returns:** `Users` object or `None` if creation failed

#### `get_user_by_telegram_id(telegram_id: str) -> Optional[Users]`

Retrieves a user by their Telegram ID.

**Parameters:**
- `telegram_id` (str): Telegram user ID

**Returns:** `Users` object or `None` if not found

#### `update_user_by_telegram_id(telegram_id: str, **kwargs) -> Optional[Users]`

Updates user information.

**Parameters:**
- `telegram_id` (str): Telegram user ID
- `**kwargs`: Fields to update (`telegram_user_name`)

**Returns:** Updated `Users` object or `None` if failed

#### `delete_user_by_telegram_id(telegram_id: str) -> bool`

Deletes a user by Telegram ID.

**Parameters:**
- `telegram_id` (str): Telegram user ID

**Returns:** `True` if deleted successfully, `False` otherwise

#### `list_all_users(limit: int = 100, offset: int = 0) -> List[Users]`

Lists all users with pagination.

**Parameters:**
- `limit` (int): Maximum number of users to return (default: 100)
- `offset` (int): Number of users to skip (default: 0)

**Returns:** List of `Users` objects

### Convenience Functions

```python
from services.users import create_user, get_user, update_user, delete_user, list_all_users

# Create user
user = create_user("123456", "username")

# Get user
user = get_user("123456")

# Update user
updated_user = update_user("123456", telegram_user_name="new_username")

# Delete user
success = delete_user("123456")

# List users
users = list_all_users(limit=50, offset=0)
```

---

## SessionService

Manages badminton session data and operations.

### Class Methods

#### `create_session(date: str, period_id: str, courts_price: float, telegram_poll_message_id: str) -> Optional[Sessions]`

Creates a new session.

**Parameters:**
- `date` (str): Session date in ISO format (YYYY-MM-DD)
- `period_id` (str): Period ID or start_date
- `courts_price` (float): Cost of courts for the session
- `telegram_poll_message_id` (str): Telegram poll message ID

**Returns:** `Sessions` object or `None` if creation failed

#### `get_session_by_date(date: str) -> Optional[Sessions]`

Retrieves a session by date.

**Parameters:**
- `date` (str): Session date in ISO format

**Returns:** `Sessions` object or `None` if not found

#### `update_session_by_date(date: str, **kwargs) -> Optional[Sessions]`

Updates session information.

**Parameters:**
- `date` (str): Session date in ISO format
- `**kwargs`: Fields to update (`courts_price`, `telegram_poll_message_id`)

**Returns:** Updated `Sessions` object or `None` if failed

#### `delete_session_by_date(date: str) -> bool`

Deletes a session by date.

**Parameters:**
- `date` (str): Session date in ISO format

**Returns:** `True` if deleted successfully, `False` otherwise

#### `list_sessions_by_period(period_start_date: str) -> List[Sessions]`

Lists all sessions for a specific period.

**Parameters:**
- `period_start_date` (str): Period start date in ISO format

**Returns:** List of `Sessions` objects

#### `get_current_session() -> Optional[Sessions]`

Gets today's session if it exists.

**Returns:** `Sessions` object for today or `None` if not found

### Convenience Functions

```python
from services.sessions import create_session, get_session, update_session, delete_session, list_sessions_by_period, get_current_session

# Create session
session = create_session("2025-08-04", "2025-08-01", 25.0, "poll_123")

# Get session
session = get_session("2025-08-04")

# Update session
updated_session = update_session("2025-08-04", courts_price=30.0)

# Delete session
success = delete_session("2025-08-04")

# List sessions by period
sessions = list_sessions_by_period("2025-08-01")

# Get current session
current = get_current_session()
```

---

## PeriodService

Manages period data with unique start_date constraint.

### Class Methods

#### `create_period(start_date: str, end_date: Optional[str] = None, total_money: Optional[int] = None) -> Optional[Periods]`

Creates a new period or returns existing period if start_date already exists.

**Parameters:**
- `start_date` (str): Period start date in ISO format (YYYY-MM-DD)
- `end_date` (Optional[str]): Period end date in ISO format (default: None)
- `total_money` (Optional[int]): Total money for the period (default: None)

**Returns:** `Periods` object or `None` if creation failed

#### `get_period_by_start_date(start_date: str) -> Optional[Periods]`

Retrieves a period by start date.

**Parameters:**
- `start_date` (str): Period start date in ISO format

**Returns:** `Periods` object or `None` if not found

#### `update_period_by_start_date(start_date: str, **kwargs) -> Optional[Periods]`

Updates period information.

**Parameters:**
- `start_date` (str): Period start date in ISO format
- `**kwargs`: Fields to update (`end_date`, `total_money`)

**Returns:** Updated `Periods` object or `None` if failed

#### `delete_period_by_start_date(start_date: str) -> Optional[Periods]`

Deletes a period by start date.

**Parameters:**
- `start_date` (str): Period start date in ISO format

**Returns:** Deleted `Periods` object or `None` if not found

#### `list_all_periods(limit: int = 100, offset: int = 0) -> List[Periods]`

Lists all periods with pagination.

**Parameters:**
- `limit` (int): Maximum number of periods to return (default: 100)
- `offset` (int): Number of periods to skip (default: 0)

**Returns:** List of `Periods` objects

#### `get_current_period() -> Optional[Periods]`

Gets the current active period (today's date falls within the period).

**Returns:** `Periods` object or `None` if no current period

#### `get_period_count() -> int`

Gets the total count of periods.

**Returns:** Number of periods as integer

### Convenience Functions

```python
from services.periods import create_period, get_period, update_period, delete_period, list_all_periods, get_current_period

# Create period
period = create_period("2025-08-01", "2025-08-31", 1000)

# Get period
period = get_period("2025-08-01")

# Update period
updated_period = update_period("2025-08-01", total_money=1200)

# Delete period
deleted_period = delete_period("2025-08-01")

# List periods
periods = list_all_periods(limit=10)

# Get current period
current = get_current_period()
```

---

## PeriodMoneyService

Manages period money records linking users to periods with amounts.

### Class Methods

#### `create_period_money(period_start_date: str, user_telegram_id: str, amount: float) -> Optional[PeriodMoneys]`

Creates a new period money record.

**Parameters:**
- `period_start_date` (str): Period start date in ISO format
- `user_telegram_id` (str): User telegram ID
- `amount` (float): Money amount

**Returns:** `PeriodMoneys` object or `None` if creation failed

#### `get_period_money_by_date(period_start_date: str, user_telegram_id: str) -> Optional[PeriodMoneys]`

Retrieves a period money record by period start date and user.

**Parameters:**
- `period_start_date` (str): Period start date in ISO format
- `user_telegram_id` (str): User telegram ID

**Returns:** `PeriodMoneys` object or `None` if not found

#### `get_period_money_by_id(period_money_id: str) -> Optional[PeriodMoneys]`

Retrieves a period money record by ID (legacy method).

**Parameters:**
- `period_money_id` (str): Period money record ID

**Returns:** `PeriodMoneys` object or `None` if not found

#### `update_period_money_by_date(period_start_date: str, user_telegram_id: str, **kwargs) -> Optional[PeriodMoneys]`

Updates period money information by period start date and user.

**Parameters:**
- `period_start_date` (str): Period start date in ISO format
- `user_telegram_id` (str): User telegram ID
- `**kwargs`: Fields to update (`amount`)

**Returns:** Updated `PeriodMoneys` object or `None` if failed

#### `update_period_money_by_id(period_money_id: str, **kwargs) -> Optional[PeriodMoneys]`

Updates period money information by ID (legacy method).

**Parameters:**
- `period_money_id` (str): Period money record ID
- `**kwargs`: Fields to update (`amount`)

**Returns:** Updated `PeriodMoneys` object or `None` if failed

#### `delete_period_money_by_date(period_start_date: str, user_telegram_id: str) -> bool`

Deletes a period money record by period start date and user.

**Parameters:**
- `period_start_date` (str): Period start date in ISO format
- `user_telegram_id` (str): User telegram ID

**Returns:** `True` if deleted successfully, `False` otherwise

#### `delete_period_money_by_id(period_money_id: str) -> bool`

Deletes a period money record by ID (legacy method).

**Parameters:**
- `period_money_id` (str): Period money record ID

**Returns:** `True` if deleted successfully, `False` otherwise

#### `list_period_moneys_by_period(period_start_date: str) -> List[PeriodMoneys]`

Lists all period money records for a specific period.

**Parameters:**
- `period_start_date` (str): Period start date in ISO format

**Returns:** List of `PeriodMoneys` objects

#### `list_period_moneys_by_user(user_telegram_id: str) -> List[PeriodMoneys]`

Lists all period money records for a specific user.

**Parameters:**
- `user_telegram_id` (str): User telegram ID

**Returns:** List of `PeriodMoneys` objects

#### `get_total_money_for_period(period_start_date: str) -> float`

Calculates total money for a specific period.

**Parameters:**
- `period_start_date` (str): Period start date in ISO format

**Returns:** Total money amount as float

### Convenience Functions

```python
from services.period_moneys import create_period_money, get_period_money, get_period_money_by_id, update_period_money, update_period_money_by_id, delete_period_money, delete_period_money_by_id, list_period_moneys_by_period, list_period_moneys_by_user, get_total_money_for_period

# Create period money
period_money = create_period_money("2025-08-01", "123456", 50.0)

# Get period money by date and user (primary method)
period_money = get_period_money("2025-08-01", "123456")

# Get period money by ID (legacy method)  
period_money = get_period_money_by_id("period_money_id")

# Update period money by date and user (primary method)
updated = update_period_money("2025-08-01", "123456", amount=75.0)

# Update period money by ID (legacy method)
updated = update_period_money_by_id("period_money_id", amount=75.0)

# Delete period money by date and user (primary method)
success = delete_period_money("2025-08-01", "123456")

# Delete period money by ID (legacy method)
success = delete_period_money_by_id("period_money_id")

# List by period
period_moneys = list_period_moneys_by_period("2025-08-01")

# List by user
user_moneys = list_period_moneys_by_user("123456")

# Get total for period
total = get_total_money_for_period("2025-08-01")
```

---

## SessionParticipantService

Manages session participation, tracking users in sessions with payment status and additional participants.

### Class Methods

#### `create_participant(user_telegram_id: str, session_date: str, additional_participants: int = 0) -> Optional[SessionParticipants]`

Creates a new session participant or returns existing participant.

**Parameters:**
- `user_telegram_id` (str): User telegram ID
- `session_date` (str): Session date in ISO format
- `additional_participants` (int): Number of additional participants brought by user (default: 0)

**Returns:** `SessionParticipants` object or `None` if creation failed

#### `get_participant_by_id(participant_id: str) -> Optional[SessionParticipants]`

Retrieves a session participant by ID.

**Parameters:**
- `participant_id` (str): Participant record ID

**Returns:** `SessionParticipants` object or `None` if not found

#### `get_participant_by_user_and_session(user_telegram_id: str, session_date: str) -> Optional[SessionParticipants]`

Retrieves a session participant by user and session.

**Parameters:**
- `user_telegram_id` (str): User telegram ID
- `session_date` (str): Session date in ISO format

**Returns:** `SessionParticipants` object or `None` if not found

#### `update_participant_by_id(participant_id: str, **kwargs) -> Optional[SessionParticipants]`

Updates participant information by ID.

**Parameters:**
- `participant_id` (str): Participant record ID
- `**kwargs`: Fields to update (`additional_participants`)

**Returns:** Updated `SessionParticipants` object or `None` if failed

#### `update_participant_by_user_and_session(user_telegram_id: str, session_date: str, **kwargs) -> Optional[SessionParticipants]`

Updates participant information by user and session.

**Parameters:**
- `user_telegram_id` (str): User telegram ID
- `session_date` (str): Session date in ISO format
- `**kwargs`: Fields to update (`additional_participants`)

**Returns:** Updated `SessionParticipants` object or `None` if failed

#### `delete_participant_by_id(participant_id: str) -> bool`

Deletes a session participant by ID.

**Parameters:**
- `participant_id` (str): Participant record ID

**Returns:** `True` if deleted successfully, `False` otherwise

#### `delete_participant_by_user_and_session(user_telegram_id: str, session_date: str) -> bool`

Deletes a session participant by user and session.

**Parameters:**
- `user_telegram_id` (str): User telegram ID
- `session_date` (str): Session date in ISO format

**Returns:** `True` if deleted successfully, `False` otherwise

#### `list_participants_by_session(session_date: str) -> List[SessionParticipants]`

Lists all participants for a specific session.

**Parameters:**
- `session_date` (str): Session date in ISO format

**Returns:** List of `SessionParticipants` objects

#### `list_participants_by_user(user_telegram_id: str) -> List[SessionParticipants]`

Lists all sessions a user has participated in.

**Parameters:**
- `user_telegram_id` (str): User telegram ID

**Returns:** List of `SessionParticipants` objects

#### `list_all_participants(limit: int = 100, offset: int = 0) -> List[SessionParticipants]`

Lists all session participants with pagination.

**Parameters:**
- `limit` (int): Maximum number of participants to return (default: 100)
- `offset` (int): Number of participants to skip (default: 0)

**Returns:** List of `SessionParticipants` objects

#### `get_participants_count_by_session(session_date: str) -> int`

Gets total number of participants (including additional) for a session.

**Parameters:**
- `session_date` (str): Session date in ISO format

**Returns:** Total participant count as integer

#### `update_additional_participants(user_telegram_id: str, session_date: str, additional_count: int) -> Optional[SessionParticipants]`

Updates the number of additional participants for a user.

**Parameters:**
- `user_telegram_id` (str): User telegram ID
- `session_date` (str): Session date in ISO format
- `additional_count` (int): New additional participants count

**Returns:** Updated `SessionParticipants` object or `None` if failed

### Convenience Functions

```python
from services.session_participants import (
    create_participant, get_participant, get_participant_by_user_and_session,
    update_participant, delete_participant, list_session_participants,
    list_user_participations, get_session_participant_count,
    update_additional_participants
)

# Create participant
participant = create_participant("123456", "2025-08-04", additional_participants=2)

# Get participant
participant = get_participant("participant_id")
participant = get_participant_by_user_and_session("123456", "2025-08-04")

# Update participant
updated = update_participant("participant_id")

# Delete participant
success = delete_participant("participant_id")

# List participants
session_participants = list_session_participants("2025-08-04")
user_participations = list_user_participations("123456")

# Get counts and payment status
total_count = get_session_participant_count("2025-08-04")

# Payment operations
update_additional_participants("123456", "2025-08-04", 3)
```

---

## Usage Examples

### Complete Workflow Example

```python
from services.users import create_user
from services.periods import create_period
from services.sessions import create_session
from services.session_participants import create_participant
from services.period_moneys import create_period_money

# 1. Create users
user1 = create_user("123456", "john_doe")
user2 = create_user("789012", "jane_smith")

# 2. Create a period
period = create_period("2025-08-01", "2025-08-31", 1000)

# 3. Create a session
session = create_session("2025-08-04", "2025-08-01", 25.0, "poll_123")

# 4. Add participants to session
participant1 = create_participant("123456", "2025-08-04", additional_participants=1)
participant2 = create_participant("789012", "2025-08-04", additional_participants=0)


# 6. Record period money
period_money1 = create_period_money("2025-08-01", "123456", 50.0)
period_money2 = create_period_money("2025-08-01", "789012", 25.0)
```

### Query Examples

```python
from services.users import list_all_users
from services.sessions import list_sessions_by_period, get_current_session
from services.session_participants import get_session_participant_count
from services.period_moneys import get_total_money_for_period

# Get all users
all_users = list_all_users(limit=50)

# Get sessions for a period
period_sessions = list_sessions_by_period("2025-08-01")

# Get current session
current_session = get_current_session()

# Get participant statistics
total_participants = get_session_participant_count("2025-08-04")

# Get financial information
total_money = get_total_money_for_period("2025-08-01")
```

---

## Error Handling

All services implement comprehensive error handling:

### Return Values
- **Success**: Returns the requested object or `True` for delete operations
- **Not Found**: Returns `None` for get operations, `False` for delete operations
- **Validation Error**: Returns `None` and logs validation errors
- **Database Error**: Returns `None`/`False` and logs database errors

### Logging
All services use Python logging to record:
- **INFO**: Successful operations
- **WARNING**: Duplicate creation attempts, soft errors
- **ERROR**: Failed operations, validation errors, database errors
- **DEBUG**: Detailed operation information

### Exception Handling
Services handle these MongoEngine exceptions:
- `DoesNotExist`: When referenced objects are not found
- `ValidationError`: When data validation fails
- `MultipleObjectsReturned`: When unique queries return multiple results
- `NotUniqueError`: When unique constraints are violated

### Best Practices
1. Always check return values for `None` before using objects
2. Handle boolean returns appropriately for delete operations
3. Use try-catch blocks for additional error handling if needed
4. Check logs for detailed error information
5. Validate input parameters before calling service methods

---

## Database Relationships

### Entity Relationships
- **Users** ↔ **SessionParticipants** (One-to-Many)
- **Sessions** ↔ **SessionParticipants** (One-to-Many)
- **Periods** ↔ **Sessions** (One-to-Many)
- **Periods** ↔ **PeriodMoneys** (One-to-Many)
- **Users** ↔ **PeriodMoneys** (One-to-Many)

### Cascade Deletes
- Deleting a **User** will delete all related **SessionParticipants** and **PeriodMoneys**
- Deleting a **Session** will delete all related **SessionParticipants**
- Deleting a **Period** will delete all related **Sessions** and **PeriodMoneys**

---

*This documentation covers all available services in the Botminton application. For implementation details, refer to the individual service files in the `/services` directory.*
