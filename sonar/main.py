import argparse
import logging.config
import dbm
import shelve
import sys
import textwrap

import sonar.database
import sonar.cli as cli
from sonar.include import Constants


def tool(parser):
    subparser = parser.add_parser("tool", help="Manage sonar tools", add_help=False)
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    # def add():
    #     command = subsubparser.add_parser(
    #         "add",
    #         help="Add a tool to sonar's database",
    #         add_help=False,
    #         description=textwrap.dedent(
    #             f"""Adds a tool to sonar's database."""
    #         ),
    #     )
    #     command_group = command.add_argument_group("Arguments")
    #     command_group.add_argument("type", type=str, help="Type of tool to add")
    #     command_group.add_argument("version", type=str, help="version of tool")
    #     command_group.add_argument(
    #         "cad_executable", type=str, help="Name of the cad tool executable"
    #     )
    #     command_group.add_argument(
    #         "sim_executable", type=str, help="Name of the sim tool executable"
    #     )
    #     command_group.add_argument(
    #         "hls_executable", type=str, help="Name of the hls tool executable"
    #     )
    #     command_group.add_argument(
    #         "script", type=str, help="Shell commands to setup using the tools"
    #     )
    #     # command_group.add_argument(
    #     #     "arg", type=str, nargs="+", help="Value to set to variable"
    #     # )
    #     command.set_defaults(func=cli.Tool.add)
    #     add_help(command)

    # def remove():
    #     command = subsubparser.add_parser(
    #         "remove",
    #         help="Remove a tool from sonar's database",
    #         add_help=False,
    #         description=f"""Removes a tool from sonar's database.

    #         The type must be one of: {tool_types}.
    #         """,
    #     )
    #     command_group = command.add_argument_group("Arguments")
    #     command_group.add_argument("type", type=str, help="Type of tool to remove")
    #     command_group.add_argument("ID", type=str, help="ID of tool")
    #     command.set_defaults(func=cli.Tool.remove)
    #     add_help(command)

    # def edit():
    #     command = subsubparser.add_parser(
    #         "edit",
    #         help="Edit a tool in sonar's database",
    #         add_help=False,
    #         description=f"""Removes a tool from sonar's database.

    #         The type must be one of: {tool_types}.
    #         """,
    #     )
    #     command_group = command.add_argument_group("Arguments")
    #     command_group.add_argument("type", type=str, help="Type of tool to edit")
    #     command_group.add_argument("ID", type=str, help="ID of tool")
    #     command_group.add_argument("value", type=str, help="Value to set to variable")
    #     command.set_defaults(func=cli.Tool.edit)
    #     add_help(command)

    def show():
        command = subsubparser.add_parser(
            "show",
            help="Show sonar's database",
            add_help=False,
            description="Shows sonar's database",
        )
        command.set_defaults(func=cli.Tool.show)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Clear sonar's database and reset it to default",
            add_help=False,
            description="Clears sonar's environment database and resets it to default",
        )
        command.set_defaults(func=cli.Tool.clear)
        add_help(command)

    # add()
    # remove()
    # edit()
    show()
    clear()
    add_help(subparser)


def env(parser):
    subparser = parser.add_parser("env", help="Manage sonar envs", add_help=False)
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    def verify_tool(arg: str):
        split = arg.split(":")
        if len(split) == 2 and split[1] != "":
            return tuple(split)
        else:
            msg = f"Tool must be in the format <tool>:<version>, not {arg}"
            raise argparse.ArgumentTypeError(msg)

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
        command_group.add_argument(
            "cad", type=verify_tool, help="CAD tool. In the format <tool>:<version>"
        )
        command_group.add_argument(
            "sim", type=verify_tool, help="Sim tool. In the format <tool>:<version>"
        )
        command_group.add_argument(
            "hls", type=verify_tool, help="HLS tool. In the format <tool>:<version>"
        )
        command.set_defaults(func=cli.Env.add)
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
        command.set_defaults(func=cli.Env.remove)
        add_help(command)

    # def edit():
    #     command = subsubparser.add_parser(
    #         "edit",
    #         help="Edit an env",
    #         add_help=False,
    #         description="Edits an env elements",
    #     )
    #     command_group = command.add_argument_group("Arguments")
    #     command_group.add_argument("name", type=str, help="Name of env")
    #     command_group.add_argument("cad", type=str, help="CAD tool")
    #     command_group.add_argument("sim", type=str, help="Sim tool")
    #     command_group.add_argument("hls", type=str, help="HLS tool")
    #     command_group.add_argument("repo", type=str, help="Repository")
    #     command_group.add_argument("board", type=str, help="Board")
    #     command.set_defaults(func=cli.Env.edit)
    #     add_help(command)

    def show():
        command = subsubparser.add_parser(
            "show",
            help="Show sonar's envs",
            add_help=False,
            description="Shows sonar's envs",
        )
        command.set_defaults(func=cli.Env.show)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Clear sonar's envs",
            add_help=False,
            description="Clears sonar's envs",
        )
        command.set_defaults(func=cli.Env.clear)
        add_help(command)

    def activate():
        command = subsubparser.add_parser(
            "activate",
            help="Activate an env",
            add_help=False,
            description="Activates an env",
        )

        command_group = command.add_argument_group("Arguments")
        command_group.add_argument(
            "env", type=str, help="Name of the env to activate",
        )
        command.set_defaults(func=cli.Env.activate)
        add_help(command)

    add()
    remove()
    # edit()
    show()
    clear()
    activate()
    add_help(subparser)


def board(parser):
    subparser = parser.add_parser(
        "board", help="Manage sonar board definitions", add_help=False
    )
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    def add():
        command = subsubparser.add_parser(
            "add",
            help="Add a board to sonar",
            add_help=False,
            description=textwrap.dedent(
                f"""\
                Adds a board to sonar's database
                """
            ),
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument("path", type=str, help="Path to board definition")
        command.set_defaults(func=cli.Board.add)
        add_help(command)

    # def remove():
    #     command = subsubparser.add_parser(
    #         "remove",
    #         help="Remove an env",
    #         add_help=False,
    #         description="Removes an env",
    #     )
    #     command_group = command.add_argument_group("Arguments")
    #     command_group.add_argument("name", type=str, help="Name of env to remove")
    #     command.set_defaults(func=cli.Env.remove)
    #     add_help(command)

    # def edit():
    #     command = subsubparser.add_parser(
    #         "edit",
    #         help="Edit an env",
    #         add_help=False,
    #         description="Edits an env elements",
    #     )
    #     command_group = command.add_argument_group("Arguments")
    #     command_group.add_argument("name", type=str, help="Name of env")
    #     command_group.add_argument("cad", type=str, help="CAD tool")
    #     command_group.add_argument("sim", type=str, help="Sim tool")
    #     command_group.add_argument("hls", type=str, help="HLS tool")
    #     command_group.add_argument("repo", type=str, help="Repository")
    #     command_group.add_argument("board", type=str, help="Board")
    #     command.set_defaults(func=cli.Env.edit)
    #     add_help(command)

    def show():
        command = subsubparser.add_parser(
            "show",
            help="Show sonar's boards",
            add_help=False,
            description="Shows sonar's boards",
        )
        command.set_defaults(func=cli.Board.show)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Clear sonar's boards",
            add_help=False,
            description="Clears sonar's boards",
        )
        command.set_defaults(func=cli.Board.clear)
        add_help(command)

    def activate():
        command = subsubparser.add_parser(
            "activate",
            help="Activate a board",
            add_help=False,
            description="Activates a board",
        )

        command_group = command.add_argument_group("Arguments")
        command_group.add_argument(
            "board", type=str, help="Name of the board to activate",
        )
        command.set_defaults(func=cli.Board.activate)
        add_help(command)

    add()
    show()
    clear()
    activate()
    add_help(subparser)


def repo(parser):
    subparser = parser.add_parser("repo", help="Manage sonar repos", add_help=False)
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    def add():
        command = subsubparser.add_parser(
            "add",
            help="Add the repo to sonar",
            add_help=False,
            description=textwrap.dedent(
                f"""\
                Adds the current repo to sonar's database
                """
            ),
        )
        command.set_defaults(func=cli.Repo.add)
        add_help(command)

    # def remove():
    #     command = subsubparser.add_parser(
    #         "remove",
    #         help="Remove an env",
    #         add_help=False,
    #         description="Removes an env",
    #     )
    #     command_group = command.add_argument_group("Arguments")
    #     command_group.add_argument("name", type=str, help="Name of env to remove")
    #     command.set_defaults(func=cli.Env.remove)
    #     add_help(command)

    # def edit():
    #     command = subsubparser.add_parser(
    #         "edit",
    #         help="Edit an env",
    #         add_help=False,
    #         description="Edits an env elements",
    #     )
    #     command_group = command.add_argument_group("Arguments")
    #     command_group.add_argument("name", type=str, help="Name of env")
    #     command_group.add_argument("cad", type=str, help="CAD tool")
    #     command_group.add_argument("sim", type=str, help="Sim tool")
    #     command_group.add_argument("hls", type=str, help="HLS tool")
    #     command_group.add_argument("repo", type=str, help="Repository")
    #     command_group.add_argument("board", type=str, help="Board")
    #     command.set_defaults(func=cli.Env.edit)
    #     add_help(command)

    def show():
        command = subsubparser.add_parser(
            "show",
            help="Show sonar reps",
            add_help=False,
            description="Shows sonar repos",
        )
        command.set_defaults(func=cli.Repo.show)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Clear sonar's repos",
            add_help=False,
            description="Clears sonar's repos",
        )
        command.set_defaults(func=cli.Repo.clear)
        add_help(command)

    def activate():
        command = subsubparser.add_parser(
            "activate",
            help="Activate a repo",
            add_help=False,
            description="Activates a repo",
        )

        command_group = command.add_argument_group("Arguments")
        command_group.add_argument(
            "repo", type=str, help="Name of the repo to activate",
        )
        command.set_defaults(func=cli.Repo.activate)
        add_help(command)

    add()
    show()
    clear()
    activate()
    add_help(subparser)


def project(parser):
    subparser = parser.add_parser(
        "project", help="Manipulate the active repo", add_help=False
    )
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    def add():
        command = subsubparser.add_parser(
            "add",
            help="Add an IP directory",
            add_help=False,
            description=textwrap.dedent(
                f"""\
                Adds an IP directory
                """
            ),
        )

        command_group = command.add_argument_group("Arguments")
        command_group.add_argument(
            "name", type=str, help="Name of the directory",
        )
        command.set_defaults(func=cli.Project.add)
        add_help(command)

    add()
    add_help(subparser)


def add_help(parser):
    command_group = parser.add_argument_group("Options")
    command_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )


def init(parser):
    subparser = parser.add_parser("init", help="Initialize sonar")

    subparser.set_defaults(func=cli.Init.one_time_setup)
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
        command.set_defaults(func=cli.Init.vivado)
        add_help(command)

    def repo():
        command = subsubparser.add_parser(
            "repo",
            help="Create a new sonar repository",
            add_help=False,
            description="Creates a new sonar repository",
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument(
            "-p", "--path", type=str, help="Path to create repository"
        )
        command.set_defaults(func=cli.Init.repo)
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
    # activate(subparser)
    tool(subparser)
    init(subparser)
    env(subparser)
    board(subparser)
    repo(subparser)
    project(subparser)

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
        cli.Init.one_time_setup(None)
    else:
        db.close()


def main():
    args = parse_args()

    check_database()
    configure_logging()

    args.func(args)
    sys.exit(0)
