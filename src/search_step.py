from enum import Enum, auto


class SearchStep(Enum):
    IDLE = auto()
    PICKING = auto()
    PREVIEWING = auto()
    TRANSPOSING = auto()
