from enum import IntEnum, unique, auto
from pathlib import Path
import os


@unique
class ReturnValue(IntEnum):
    SONAR_OK = 0
    SONAR_INVALID_ARG = auto()
    SONAR_INVALID_NUMBER_OF_ARGS = auto()
    SONAR_NONEXISTENT_PATH = auto()


def init_constants(cls):
    cls.add_derived()
    return cls


@init_constants
class Constants:
    SONAR_BASE_PATH = Path.home()
    SONAR_DIRECTORY = Path(".sonar")
    SONAR_LOG_FILE = Path("sonar.log")
    SONAR_RC_FILE = Path(".sonarrc")
    SONAR_DB = Path("sonar_db")
    SONAR_BASH_SCRIPTS = Path("shell/bash")
    SONAR_MAIN_SOURCE = Path("sonar.sh")
    SONAR_ENV_SOURCE = Path("sonar_env.sh")

    @classmethod
    def add_derived(cls):
        cls.SONAR_PATH = cls.SONAR_BASE_PATH.joinpath(cls.SONAR_DIRECTORY)
        cls.SONAR_LOG_PATH = cls.SONAR_PATH.joinpath(cls.SONAR_LOG_FILE)
        cls.SONAR_DB_PATH = str(
            cls.SONAR_PATH.joinpath(cls.SONAR_DB)
        )  # shelve doesn't like pathlib
        cls.SONAR_BASH_PATH = cls.SONAR_PATH.joinpath(cls.SONAR_BASH_SCRIPTS)
        cls.SONAR_BASH_ENV_SOURCE = cls.SONAR_BASH_PATH.joinpath(cls.SONAR_ENV_SOURCE)


def sonarrc_exists():
    if "SONAR_REPO" in os.environ:
        if os.path.exists(os.path.join(os.environ["SONAR_REPO"], Constants.SONAR_RC)):
            return True
        return False
    return False
