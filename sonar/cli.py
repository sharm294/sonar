import argparse
import textwrap

import sonar.api as api


def activate(parser: argparse._SubParsersAction):
    subparser: argparse.ArgumentParser = parser.add_parser(
        "activate", help="Activate environment settings", add_help=False
    )

    command_group = subparser.add_argument_group("Environment")
    command_group.add_argument(
        "env", type=str, nargs="?", default=None, help="Name of the env to activate",
    )
    command_group = subparser.add_argument_group("Custom")
    command_group.add_argument("--tool")
    command_group.add_argument("--cad")
    command_group.add_argument("--hls")
    command_group.add_argument("--sim")
    subparser.set_defaults(func=api.activate)
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
        command_group.add_argument(
            "cad", type=str, help="CAD tool. In the format <tool>:<version>"
        )
        command_group.add_argument(
            "sim", type=str, help="Sim tool. In the format <tool>:<version>"
        )
        command_group.add_argument(
            "hls", type=str, help="HLS tool. In the format <tool>:<version>"
        )
        command_group.add_argument("board", type=str, help="Board")
        command_group.add_argument("repo", type=str, help="Repo")
        command.set_defaults(func=api.Env.add)
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
        command.set_defaults(func=api.Env.remove)
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
    #     command.set_defaults(func=api.Env.edit)
    #     add_help(command)

    def f_list():
        command = subsubparser.add_parser(
            "list",
            help="List environments",
            add_help=False,
            description="Lists environments",
        )
        command.set_defaults(func=api.Env.f_list)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Clear sonar's envs",
            add_help=False,
            description="Clears sonar's envs",
        )
        command.set_defaults(func=api.Env.clear)
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
        command.set_defaults(func=api.Env.activate)
        add_help(command)

    activate()
    add()
    clear()
    # edit()
    remove()
    f_list()
    add_help(subparser)


def tool(parser):
    subparser = parser.add_parser("tool", help="Manage hw tools", add_help=False)
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
    #     command.set_defaults(func=api.Tool.add)
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
    #     command.set_defaults(func=api.Tool.remove)
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
    #     command.set_defaults(func=api.Tool.edit)
    #     add_help(command)

    def f_list():
        command = subsubparser.add_parser(
            "list",
            help="List sonar's database",
            add_help=False,
            description="Lists sonar's database",
        )
        command.set_defaults(func=api.Tool.f_list)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Clear sonar's database and reset it to default",
            add_help=False,
            description="Clears sonar's environment database and resets it to default",
        )
        command.set_defaults(func=api.Tool.clear)
        add_help(command)

    # add()
    # remove()
    # edit()
    clear()
    f_list()
    add_help(subparser)


def board(parser):
    subparser = parser.add_parser(
        "board", help="Manage board definitions", add_help=False
    )
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    def add():
        command = subsubparser.add_parser(
            "add",
            help="Add a board",
            add_help=False,
            description=textwrap.dedent(
                f"""\
                Adds a board to the database
                """
            ),
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument(
            "path", type=str, help="Path to directory containing board definition"
        )
        command.set_defaults(func=api.Board.add)
        add_help(command)

    def remove():
        command = subsubparser.add_parser(
            "remove",
            help="Remove a board",
            add_help=False,
            description="Removes a board from the database",
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument("name", type=str, help="Name of board to remove")
        command.set_defaults(func=api.Board.remove)
        add_help(command)

    def show():
        command = subsubparser.add_parser(
            "show",
            help="Show information about a board",
            add_help=False,
            description="Shows information about a board",
        )
        command_group = command.add_argument_group("Arguments")
        command_group.add_argument("name", type=str, help="Name of board to show")
        command.set_defaults(func=api.Board.show)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Remove all boards",
            add_help=False,
            description="Removes all boards",
        )
        command.set_defaults(func=api.Board.clear)
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
        command.set_defaults(func=api.Board.activate)
        add_help(command)

    def deactivate():
        command = subsubparser.add_parser(
            "deactivate",
            help="Deactivate the active board",
            add_help=False,
            description="Deactivates the active board",
        )

        command.set_defaults(func=api.Board.deactivate)
        add_help(command)

    def f_list():
        command = subsubparser.add_parser(
            "list",
            help="List all boards and active board",
            add_help=False,
            description="Lists all boards and active board",
        )
        command.set_defaults(func=api.Board.f_list)
        add_help(command)

    activate()
    add()
    clear()
    deactivate()
    f_list()
    remove()
    show()
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
        command.set_defaults(func=api.Repo.add)
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
    #     command.set_defaults(func=api.Env.remove)
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
    #     command.set_defaults(func=api.Env.edit)
    #     add_help(command)

    def f_list():
        command = subsubparser.add_parser(
            "list",
            help="List sonar reps",
            add_help=False,
            description="Lists sonar repos",
        )
        command.set_defaults(func=api.Repo.f_list)
        add_help(command)

    def clear():
        command = subsubparser.add_parser(
            "clear",
            help="Clear sonar's repos",
            add_help=False,
            description="Clears sonar's repos",
        )
        command.set_defaults(func=api.Repo.clear)
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
        command.set_defaults(func=api.Repo.activate)
        add_help(command)

    activate()
    add()
    clear()
    f_list()
    add_help(subparser)


def create(parser):
    subparser = parser.add_parser(
        "create", help="Manipulate the active repo", add_help=False
    )
    subsubparser = subparser.add_subparsers(title="Commands", metavar="command")

    def ip():
        command = subsubparser.add_parser(
            "ip",
            help="Create an IP directory",
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
        command.set_defaults(func=api.Create.ip)
        add_help(command)

    def repo():
        command = subsubparser.add_parser(
            "repo",
            help="Create an empty repo directory",
            add_help=False,
            description=textwrap.dedent(
                f"""\
                Create a repo directory
                """
            ),
        )

        command_group = command.add_argument_group("Arguments")
        command_group.add_argument(
            "name", type=str, help="Name of the repo",
        )
        command.set_defaults(func=api.Create.repo)
        add_help(command)

    ip()
    repo()
    add_help(subparser)


def add_help(parser):
    command_group = parser.add_argument_group("Options")
    command_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )


def init(parser):
    subparser = parser.add_parser("init", help="Initialize sonar")

    subparser.set_defaults(func=api.Init.one_time_setup)
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
        command.set_defaults(func=api.Init.vivado)
        add_help(command)

    # def repo():
    #     command = subsubparser.add_parser(
    #         "repo",
    #         help="Create a new sonar repository",
    #         add_help=False,
    #         description="Creates a new sonar repository",
    #     )
    #     command_group = command.add_argument_group("Arguments")
    #     command_group.add_argument(
    #         "-p", "--path", type=str, help="Path to create repository"
    #     )
    #     command.set_defaults(func=api.Init.repo)
    #     add_help(command)

    # repo()
    vivado()
