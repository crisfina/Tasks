from enum import Enum

class RepeatType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    SEMESTERLY = "semesterly"
    TWICE_A_YEAR = "twice_a_year"
    YEARLY = "yearly"