import argparse
import logging.config
import dbm
import shelve
import sys
import textwrap

import sonar.database
import sonar.cli as cli
from sonar.include import Constants


def activate(parser):
    subparser = parser.add_parser(
        "activate", help="Activate an environment environment"
    )

    subparser.add_argument(
        "env", type=str, help="Name of the env to activate",
    )
    subparser.set_defaults(func=cli.handle_activate)


def tool(parser):
    subparser = parser.add_parser("tool", help="Manage sonar tools", add_help=False)
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    tool_types = ", ".join(vars(sonar.database.DBtools()))

    def add():
        command = subsubparser.add_parser(
            "add",
            help="Add a tool to sonar's database",
            add_help=False,
            description=textwrap.dedent(
                f"""\
                Adds a tool to sonar's database.

                The type must be one of: {tool_types}.

                IDs must be unique within a type.
                """
            ),
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument("type", type=str, help="Type of tool to add")
        command_group.add_argument("ID", type=str, help="ID of tool")
        command_group.add_argument(
            "executable", type=str, help="Name of executable to call"
        )
        command_group.add_argument("version", type=str, help="Tool version identifier")
        command_group.add_argument(
            "script", type=str, help="Name of executable to call"
        )
        # command_group.add_argument(
        #     "arg", type=str, nargs="+", help="Value to set to variable"
        # )
        command.set_defaults(func=cli.handler_tool_add)
        add_help(command)

    def remove():
        command = subsubparser.add_parser(
            "remove",
            help="Remove a tool from sonar's database",
            add_help=False,
            description=f"""Removes a tool from sonar's database.

            The type must be one of: {tool_types}.
            """,
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument("type", type=str, help="Type of tool to remove")
        command_group.add_argument("ID", type=str, help="ID of tool")
        command.set_defaults(func=cli.handler_tool_remove)
        add_help(command)

    def edit():
        command = subsubparser.add_parser(
            "edit",
            help="Edit a tool in sonar's database",
            add_help=False,
            description=f"""Removes a tool from sonar's database.

            The type must be one of: {tool_types}.
            """,
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument("type", type=str, help="Type of tool to edit")
        command_group.add_argument("ID", type=str, help="ID of tool")
        command_group.add_argument("value", type=str, help="Value to set to variable")
        command.set_defaults(func=cli.handler_tool_edit)
        add_help(command)

    def show():
        command = subsubparser.add_parser(
            "show",
            help="Show sonar's database",
            add_help=False,
            description="Shows sonar's database",
        )
        command.set_defaults(func=cli.handler_tool_show)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Clear sonar's database and reset it to default",
            add_help=False,
            description="Clears sonar's environment database and resets it to default",
        )
        command.set_defaults(func=cli.handler_tool_clear)
        add_help(command)

    add()
    remove()
    # edit()
    show()
    clear()
    add_help(subparser)


def env(parser):
    subparser = parser.add_parser("env", help="Manage sonar envs", add_help=False)
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    def add():
        command = subsubparser.add_parser(
            "add",
            help="Add an env to sonar",
            add_help=False,
            description=textwrap.dedent(
                f"""\
                Adds an env to sonar's database that can be activated with 'sonar
                activate'. Env elements must be already added to sonar.
                """
            ),
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument("name", type=str, help="Name of env")
        command_group.add_argument("cad", type=str, help="CAD tool")
        command_group.add_argument("sim", type=str, help="Sim tool")
        command_group.add_argument("hls", type=str, help="HLS tool")
        command_group.add_argument("repo", type=str, help="Repository")
        command_group.add_argument("board", type=str, help="Board")
        command.set_defaults(func=cli.handler_env_add)
        add_help(command)

    def remove():
        command = subsubparser.add_parser(
            "remove",
            help="Remove an env",
            add_help=False,
            description="Removes an env",
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument("name", type=str, help="Name of env to remove")
        command.set_defaults(func=cli.handler_env_remove)
        add_help(command)

    def edit():
        command = subsubparser.add_parser(
            "edit",
            help="Edit an env",
            add_help=False,
            description="Edits an env elements",
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument("name", type=str, help="Name of env")
        command_group.add_argument("cad", type=str, help="CAD tool")
        command_group.add_argument("sim", type=str, help="Sim tool")
        command_group.add_argument("hls", type=str, help="HLS tool")
        command_group.add_argument("repo", type=str, help="Repository")
        command_group.add_argument("board", type=str, help="Board")
        command.set_defaults(func=cli.handler_env_edit)
        add_help(command)

    def show():
        command = subsubparser.add_parser(
            "show",
            help="Show sonar's envs",
            add_help=False,
            description="Shows sonar's envs",
        )
        command.set_defaults(func=cli.handler_env_show)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Clear sonar's envs",
            add_help=False,
            description="Clears sonar's envs",
        )
        command.set_defaults(func=cli.handler_env_clear)
        add_help(command)

    add()
    remove()
    # edit()
    show()
    clear()
    add_help(subparser)


def add_help(parser):
    command_group = parser.add_argument_group("Options")
    command_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )


def init(parser):
    subparser = parser.add_parser("init", help="Initialize sonar")

    subparser.set_defaults(func=cli.handle_init)
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    def vivado():
        command = subsubparser.add_parser(
            "vivado",
            help="Add Vivado(s) to sonar's database",
            add_help=False,
            description="Adds all Vivado versions to sonar's database automatically",
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument(
            "path", type=str, help="Path to Xilinx install folder"
        )
        command.set_defaults(func=cli.handler_init_vivado)
        add_help(command)

    vivado()


def configure_logging():
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
            "": {"level": "DEBUG", "handlers": ["consoleHandler", "fileHandler"]}
        },
    }

    logging.config.dictConfig(config)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="sonar",
        description="sonar is a tool to manage and test your hardware projects.",
        # usage="%(prog)s [-h] command [command args]",
        add_help=False,
    )
    parser.set_defaults(func=lambda x: parser.print_help())
    subparser = parser.add_subparsers(title="Commands", metavar="command")
    activate(subparser)
    tool(subparser)
    init(subparser)
    env(subparser)

    command_group = parser.add_argument_group("Options")
    command_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )
    command_group.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + sonar.__version__
    )

    return parser.parse_args()


def check_database():
    try:
        db = shelve.open(Constants.SONAR_DB_PATH, "r")
    except dbm.error:
        cli.handle_init(None)
    else:
        db.close()


def main():
    args = parse_args()

    check_database()
    configure_logging()

    args.func(args)
    sys.exit(0)
