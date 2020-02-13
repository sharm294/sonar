import logging

from sonar.include import ReturnValue

logger = logging.getLogger(__name__)

ENV_ADD_TYPES = [
    "cad_tool",
    "sim_tool",
    "hls_tool",
    "repo",
    "hls_include",
    "board",
    "part",
    "cad_version",
    "sim_version",
    "hls_version",
]


def handle_activate(args):
    print(args.profile)


def handler_env_add(args):
    if args.type not in ENV_ADD_TYPES:
        logger.error(f"{args.type} is not a valid type. See sonar env add --help")
        return ReturnValue.SONAR_INVALID_ARG
