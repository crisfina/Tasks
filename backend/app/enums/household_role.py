from enum import Enum

class HouseholdRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"