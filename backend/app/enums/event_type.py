from enum import Enum

class EventType(Enum):
    REWARD = "reward"
    PENALTY = "penalty"
    MANUAL = "manual"