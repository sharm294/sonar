"""
Broadly used functions and classes across sonar
"""

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
        cls.SONAR_CONFIG_FILE_PATH = cls.SONAR_DIRECTORY.joinpath(cls.SONAR_CONFIG_FILE)


def replace_in_file(src_file, str_to_replace, replacement_str):
    """
    Replace a string in a file and save the file back in place

    Args:
        src_file (filepath): Str or Path to a file to open
        str_to_replace (str): The string to replace
        replacement_str (str): The replacement string
    """
    with open(src_file, "r") as f:
        filedata = f.read()

    filedata = filedata.replace(str_to_replace, replacement_str)

    with open(src_file, "w") as f:
        f.write(filedata)


# https://stackoverflow.com/a/32107024
class DotDict(dict):
    """
    A dictionary that allows its members to be accessed through the dot operator
    as attributes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)
