from enum import IntEnum, unique, auto


@unique
class ReturnValue(IntEnum):
    SONAR_UNKNOWN = -1
    SONAR_OK = 0
    SONAR_INVALID_ARG = auto()
    SONAR_INVALID_NUMBER_OF_ARGS = auto()
    SONAR_NONEXISTENT_PATH = auto()
    SONAR_INVALID_PATH = auto()
    SONAR_INVALID_OP = auto()


class SonarException(Exception):
    def __init__(self, message=""):
        super().__init__(message)
        self.exit_str = ReturnValue.SONAR_UNKNOWN.name
        self.exit_code = ReturnValue.SONAR_UNKNOWN.value


class SonarInvalidArgError(SonarException):
    def __init__(self, message=""):
        super().__init__(message)
        self.exit_str = ReturnValue.SONAR_INVALID_ARG.name
        self.exit_code = ReturnValue.SONAR_INVALID_ARG.value


class SonarInvalidOpError(SonarException):
    def __init__(self, message=""):
        super().__init__(message)
        self.exit_str = ReturnValue.SONAR_INVALID_OP.name
        self.exit_code = ReturnValue.SONAR_INVALID_OP.value
