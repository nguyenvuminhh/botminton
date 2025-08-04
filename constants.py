from enum import StrEnum

class Commands(StrEnum):
    START = "start"
    PRINT_GROUP_CHAT_ID = "print_group_chat_id"
    PRINT_USER_ID = "print_user_id"
    TEST_ADMIN = "test_admin"

class PollOptions(StrEnum):
    YES = "Có"
    NO = "Không"
    PLUS_ONE = "+1"

ALL_POLL_OPTIONS = [PollOptions.YES, PollOptions.NO, PollOptions.PLUS_ONE]

POLL_OPTIONS_TO_NUMBER_MAPPING = {
    PollOptions.YES: 1,
    PollOptions.NO: 0,
    PollOptions.PLUS_ONE: 2
}