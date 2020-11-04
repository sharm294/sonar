"""
The main entry point for the sonar CLI. Here, we check the status of the
local user database and pass in the command-line arguments to their parsers.
"""

import argparse
import sys

import sonar
import sonar.api as api
import sonar.cli as cli

try:
    import argcomplete
except ImportError:
    pass


def parse_args():
    """
    Defines the command-line argument parser. All the parsing functions are in
    the CLI module

    Returns:
        args: The parsed args
    """
    parser = argparse.ArgumentParser(
        prog="sonar",
        description="sonar is a tool to manage and test your hardware projects.",
        add_help=False,
    )
    parser.set_defaults(func=lambda x: parser.print_help())
    subparser = parser.add_subparsers(title="Commands", metavar="command")
    cli.activate(subparser)
    cli.board(subparser)
    cli.create(subparser)
    cli.database(subparser)
    cli.env(subparser)
    cli.init(subparser)
    cli.repo(subparser)
    cli.tool(subparser)

    command_group = parser.add_argument_group("Options")
    command_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )
    command_group.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + sonar.__version__,
    )
    try:
        argcomplete.autocomplete(parser)
    except NameError:
        pass
    return parser.parse_args()


def main():
    """
    Main CLI usage. Parses the command-line arguments, checks the local database
    and calls the appropriate CLI function.
    """
    args = parse_args()

    api.check_database()

    args.func(args)
    sys.exit(0)
