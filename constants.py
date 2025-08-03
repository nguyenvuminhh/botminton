from enum import StrEnum

class Commands(StrEnum):
    START = "start"

class PollOptions(StrEnum):
    YES = "Có"
    NO = "Không"
    PLUS_ONE = "+1"

POLL_OPTIONS_TO_NUMBER_MAPPING = {
    PollOptions.YES: 1,
    PollOptions.NO: 0,
    PollOptions.PLUS_ONE: 2
}