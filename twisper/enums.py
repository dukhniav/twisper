from enum import Enum


class State(Enum):
    """
    Bot application states
    """
    STARTING = 1
    RUNNING = 2
    STOPPED = 3

    def __str__(self):
        return f"{self.name.lower()}"

class RunMode(Enum):
    """
    Bot runmode
    """
    LIVE = "life"
    DRY_RUN = "dry_run"

    def __str__(self):
        return f"{self.name.lower()}"

class TimerType(Enum):
    """
    Timer type
    """
    RETWEET = "retweet"
    FOLLOW = "follow"
    LIKE = "like"
    MESSAGE = "message"
    EPOCH = "epoch"

    def __str__(self):
        return f"{self.name.lower()}"
