from enum import Enum, auto
from typing import Callable


class BindingPower(Enum):
    DEFAULT = auto()
    COMMA = auto()
    ASSIGNMENT = auto()
    LOGICAL = auto()
    RELATIONAL = auto()
    ADDITIVE = auto()
    MULTIPLICATIVE = auto()
    UNARY = auto()
    CALL = auto()
    MEMBER = auto()
    PRIMARY = auto()


