from enum import StrEnum


class Commands(StrEnum):
    PRINT_GROUP_CHAT_ID = "print_group_chat_id"
    PRINT_USER_ID = "print_user_id"
    TEST_ADMIN = "test_admin"
    # Poll
    OPEN_POLL = "open_poll"
    CLOSE_POLL = "close_poll"
    # Session management
    ADD_PLAYER = "add_player"
    REMOVE_PLAYER = "remove_player"
    ADD_PLUS_ONE = "add_plus_one"
    REMOVE_PLUS_ONE = "remove_plus_one"
    SET_SLOTS = "set_slots"
    SET_VENUE = "set_venue"
    # Period management
    NEW_PERIOD = "end_current_and_start_new_period"
    PERIOD_SUMMARY = "period_summary"
    ADD_SHUTTLECOCK = "add_shuttlecock"
    # Venues
    LIST_VENUES = "list_venues"
    ADD_VENUE = "add_venue"
    # Payment tracking
    PAYMENT_STATUS = "payment_status"
    MARK_PAID = "mark_paid"
    CONFIRM_PAID = "confirm_paid"


class PollOptions(StrEnum):
    YES = "Có"
    NO = "Không"


ALL_POLL_OPTIONS = [PollOptions.YES, PollOptions.NO]

POLL_OPTIONS_TO_NUMBER_MAPPING = {
    PollOptions.YES: 1,
    PollOptions.NO: 0,
}
