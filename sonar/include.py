from enum import IntEnum, unique, auto
from pathlib import Path
import os


@unique
class ReturnValue(IntEnum):
    SONAR_OK = 0
    SONAR_INVALID_ARG = auto()


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
