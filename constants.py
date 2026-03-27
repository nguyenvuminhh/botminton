from enum import StrEnum


class Commands(StrEnum):
    PRINT_GROUP_CHAT_ID = "printgroupchatid"
    PRINT_USER_ID = "printuserid"
    TEST_ADMIN = "testadmin"
    # Poll
    OPEN_POLL = "openpoll"
    CLOSE_POLL = "closepoll"
    # Session management
    ADD_PLAYER = "addplayer"
    REMOVE_PLAYER = "removeplayer"
    ADD_PLUS_ONE = "addplusone"
    REMOVE_PLUS_ONE = "removeplusone"
    SET_SLOTS = "setslots"
    SET_VENUE = "setvenue"
    # Period management
    NEW_PERIOD = "endcurrentandstartnewperiod"
    PERIOD_SUMMARY = "periodsummary"
    ADD_SHUTTLECOCK = "addshuttlecock"
    # Venues
    LIST_VENUES = "listvenues"
    ADD_VENUE = "addvenue"
    SET_SCHEDULE = "setschedule"
    # Payment tracking
    PAYMENT_STATUS = "paymentstatus"
    MARK_PAID = "markpaid"
    CONFIRM_PAID = "confirmpaid"


class PollOptions(StrEnum):
    YES = "Có"
    NO = "Không"


ALL_POLL_OPTIONS = [PollOptions.YES, PollOptions.NO]

POLL_OPTIONS_TO_NUMBER_MAPPING = {
    PollOptions.YES: 1,
    PollOptions.NO: 0,
}
