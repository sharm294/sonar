"""
Broadly used functions and classes across sonar core
"""

import logging.config
from pathlib import Path


def init_constants(cls):
    """
    Add the derived constants to the Constants class

    Returns:
        Constants: Holds sonar constants as attributes
    """
    cls.add_derived()
    return cls


@init_constants
class Constants:
    """
    Holds sonar constants as attributes
    """

    ARGPARSE_FAILURE = 2
    SONAR_BASE_PATH = Path.home()
    SONAR_DIRECTORY = Path(".sonar")
    SONAR_LOG_FILE = Path("sonar.log")
    SONAR_CONFIG_FILE = Path(".sonar.toml")
    SONAR_DB = Path("sonar_db")
    SONAR_SHELL_SCRIPTS = Path("shell")
    SONAR_MAIN_SOURCE = Path("sonar.sh")
    SONAR_TOOL_SOURCE = Path("sonar_tool.sh")
    SONAR_BOARD_SOURCE = Path("sonar_board.sh")
    SONAR_REPO_SOURCE = Path("sonar_repo.sh")
    SONAR_IP_MAKEFILE = "sonar.mk"

    @classmethod
    def add_derived(cls):
        """
        This method of adding the derived constants allows overriding the base
        attributes (above) and then defining the derived attributes based on
        their new values. This functionality is used in the tests to define a
        new SONAR_BASE_PATH for example.
        """
        cls.SONAR_PATH = cls.SONAR_BASE_PATH.joinpath(cls.SONAR_DIRECTORY)
        cls.SONAR_LOG_PATH = cls.SONAR_PATH.joinpath(cls.SONAR_LOG_FILE)
        cls.SONAR_DB_PATH = str(
            cls.SONAR_PATH.joinpath(cls.SONAR_DB)
        )  # shelve doesn't like pathlib
        cls.SONAR_SHELL_PATH = cls.SONAR_PATH.joinpath(cls.SONAR_SHELL_SCRIPTS)
        cls.SONAR_SHELL_MAIN_SOURCE = cls.SONAR_SHELL_PATH.joinpath(
            cls.SONAR_MAIN_SOURCE
        )
        cls.SONAR_SHELL_TOOL_SOURCE = cls.SONAR_SHELL_PATH.joinpath(
            cls.SONAR_TOOL_SOURCE
        )
        cls.SONAR_SHELL_BOARD_SOURCE = cls.SONAR_SHELL_PATH.joinpath(
            cls.SONAR_BOARD_SOURCE
        )
        cls.SONAR_SHELL_REPO_SOURCE = cls.SONAR_SHELL_PATH.joinpath(
            cls.SONAR_REPO_SOURCE
        )
        cls.SONAR_CONFIG_FILE_PATH = cls.SONAR_DIRECTORY.joinpath(
            cls.SONAR_CONFIG_FILE
        )


def configure_logging():
    """
    Defines a standard set of logging practices across sonar
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "fileFormatter": {
                "format": "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s",
                "datafmt": "%H:%M:%S",
            },
            "consoleFormatter": {
                "format": "%(levelname)s - %(message)s",
                "datafmt": "",
            },
        },
        "handlers": {
            "consoleHandler": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": "consoleFormatter",
                "stream": "ext://sys.stdout",
            },
            "fileHandler": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "fileFormatter",
                "filename": Constants.SONAR_LOG_PATH,
                "mode": "a",
            },
        },
        "loggers": {
            "": {
                "level": "DEBUG",
                "handlers": ["consoleHandler", "fileHandler"],
            }
        },
    }

    logging.config.dictConfig(config)
