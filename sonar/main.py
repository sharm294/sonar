import argparse
import argcomplete

import sys

import sonar
import sonar.api as api
import sonar.cli as cli


def parse_args():
    parser = argparse.ArgumentParser(
        prog="sonar",
        description="sonar is a tool to manage and test your hardware projects.",
        # usage="%(prog)s [-h] command [command args]",
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
    cli.ip(subparser)
    cli.repo(subparser)
    cli.tool(subparser)

    command_group = parser.add_argument_group("Options")
    command_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )
    command_group.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + sonar.__version__
    )

    argcomplete.autocomplete(parser)
    return parser.parse_args()


def main():
    args = parse_args()

    api.check_database()
    api.configure_logging()

    args.func(args)
    sys.exit(0)
