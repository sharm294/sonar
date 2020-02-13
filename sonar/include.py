from enum import IntEnum, unique, auto


@unique
class ReturnValue(IntEnum):
    SONAR_OK = 0
    SONAR_INVALID_ARG = auto()
