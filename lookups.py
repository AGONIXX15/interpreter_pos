from enum import Enum, auto


class BindingPower(Enum):
    DEFAULT = auto()
    COMMA = auto()
    ASSIGNMENT = auto()
    LOGICAL = auto()
    UNARY = auto()
    RELATIONAL = auto()
    ADDITIVE = auto()
    MULTIPLICATIVE = auto()
    EXPONENTIAL = auto()
    CALL = auto()
    MEMBER = auto()
    PRIMARY = auto()
