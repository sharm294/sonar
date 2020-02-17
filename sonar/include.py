from enum import IntEnum, unique, auto
from pathlib import Path
import os


@unique
class ReturnValue(IntEnum):
    SONAR_OK = 0
    SONAR_INVALID_ARG = auto()
    SONAR_INVALID_NUMBER_OF_ARGS = auto()
    SONAR_NONEXISTENT_PATH = auto()


class Constants:
    SONAR_DIRECTORY = os.path.join(str(Path.home()), ".sonar")
    SONAR_LOG = os.path.join(SONAR_DIRECTORY, "sonar.log")
    SONAR_RC = ".sonarrc"
    SONAR_DATABASE = os.path.join(SONAR_DIRECTORY, "sonar_db")


def sonarrc_exists():
    if "SONAR_REPO" in os.environ:
        if os.path.exists(os.path.join(os.environ["SONAR_REPO"], Constants.SONAR_RC)):
            return True
        return False
    return False


class DotDict(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]
