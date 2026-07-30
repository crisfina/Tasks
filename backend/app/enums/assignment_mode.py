from enum import Enum

class AssignmentMode(Enum):
    NONE = "none"
    MANUAL = "manual"
    FIXED = "fixed"
    ALTERNATING = "alternating"
    LOWEST_SCORE = "lowest_score"
    RANDOM = "random"
    LEAST_BUSY = "least_busy"
    SHORTEST_ESTIMATED_TIME = "shortest_estimated_time"