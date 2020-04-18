from pathlib import Path


def init_constants(cls):
    cls.add_derived()
    return cls


@init_constants
class Constants:
    ARGPARSE_FAILURE = 2
    SONAR_BASE_PATH = Path.home()
    SONAR_DIRECTORY = Path(".sonar")
    SONAR_LOG_FILE = Path("sonar.log")
    SONAR_CONFIG_FILE = Path("init.toml")
    SONAR_DB = Path("sonar_db")
    SONAR_SHELL_SCRIPTS = Path("shell")
    SONAR_MAIN_SOURCE = Path("sonar.sh")
    SONAR_TOOL_SOURCE = Path("sonar_tool.sh")
    SONAR_BOARD_SOURCE = Path("sonar_board.sh")
    SONAR_REPO_SOURCE = Path("sonar_repo.sh")
    SONAR_IP_MAKEFILE = "sonar.mk"

    @classmethod
    def add_derived(cls):
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


# def sonarrc_exists():
#     if "SONAR_REPO" in os.environ:
#         if os.path.exists(os.path.join(os.environ["SONAR_REPO"], Constants.SONAR_RC)):
#             return True
#         return False
#     return False
