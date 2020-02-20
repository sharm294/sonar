import logging
import os
import shelve
import shutil

import sonar.database as database
from sonar.include import ReturnValue, Constants

logger = logging.getLogger(__name__)


def handle_activate(args):
    with shelve.open(Constants.SONAR_DATABASE) as db:
        env = db["env"][args.env]
        with open(Constants.SONAR_BASH_ENV_SOURCE, "w") as f:
            script = []
            for key in ["cad_tool", "sim_tool", "hls_tool"]:
                tool_id = env[key]
                tool = db["tool"][key][tool_id]
                if tool.script not in script:
                    script.append(tool.script)
            f.write("\n".join(script))

    return ReturnValue.SONAR_OK


def handler_tool_add(args):
    if args.type not in vars(database.Tools()):
        logger.error(f"{args.type} is not a valid type. See sonar env add --help")
        return ReturnValue.SONAR_INVALID_ARG

    with shelve.open(Constants.SONAR_DATABASE) as db:
        tools = db["tool"]
        _dict = tools[args.type]
        value = database.Tool(args.executable, args.version, args.script)
        _dict[args.ID] = value
        tools[args.type] = _dict
        db["tool"] = tools

    return ReturnValue.SONAR_OK


def handler_tool_remove(args):
    if args.type not in vars(database.Tools()):
        logger.error(f"{args.type} is not a valid type. See sonar env remove --help")
        return ReturnValue.SONAR_INVALID_ARG

    with shelve.open(Constants.SONAR_DATABASE) as db:
        tools = db["tool"]
        _dict = tools[args.type]
        del _dict[args.name]
        tools[args.type] = _dict
        db["tool"] = tools

    return ReturnValue.SONAR_OK


def handler_tool_edit(args):
    if args.type not in vars(database.Tools()):
        logger.error(f"{args.type} is not a valid type. See sonar env remove --help")
        return ReturnValue.SONAR_INVALID_ARG

    with shelve.open(Constants.SONAR_DATABASE) as db:
        tools = db["tool"]
        _dict = tools[args.type]
        _dict[args.name] = args.value
        tools[args.type] = _dict
        db["tool"] = tools

    return ReturnValue.SONAR_OK


def handler_tool_show(args):
    with shelve.open(Constants.SONAR_DATABASE) as db:
        tools = db["tool"]
        print(tools)

    return ReturnValue.SONAR_OK


def handler_tool_clear(args):
    with shelve.open(Constants.SONAR_DATABASE) as db:
        db["tool"] = database.Tools()

    return ReturnValue.SONAR_OK


def handler_env_add(args):
    with shelve.open(Constants.SONAR_DATABASE) as db:
        env = db["env"]
        env[args.name] = database.Environment(
            args.cad_tool, args.sim_tool, args.hls_tool, args.repo, args.board
        )
        db["env"] = env

    return ReturnValue.SONAR_OK


def handler_env_remove(args):
    with shelve.open(Constants.SONAR_DATABASE) as db:
        env = db["env"]
        del env[args.name]
        db["env"] = env

    return ReturnValue.SONAR_OK


def handler_env_edit(args):
    with shelve.open(Constants.SONAR_DATABASE) as db:
        env = db["env"]
        env[args.name] = database.Environment(
            args.cad_tool, args.sim_tool, args.hls_tool, args.repo, args.board
        )
        db["env"] = env

    return ReturnValue.SONAR_OK


def handler_env_show(args):
    with shelve.open(Constants.SONAR_DATABASE) as db:
        env = db["env"]
        print(env)

    return ReturnValue.SONAR_OK


def handler_env_clear(args):
    with shelve.open(Constants.SONAR_DATABASE) as db:
        db["env"] = {}

    return ReturnValue.SONAR_OK


def handle_init(args):
    os.makedirs(Constants.SONAR_DIRECTORY, exist_ok=True)

    src_dir = os.path.join(os.path.dirname(__file__), "shell")
    dst_dir = os.path.join(Constants.SONAR_DIRECTORY, "shell")
    shutil.copytree(src_dir, dst_dir)
    retval = handler_tool_clear(args)
    retval = handler_env_clear(args)

    return retval


def handler_init_vivado(args):
    xilinx_path = os.path.abspath(args.path)

    vivado_path = os.path.join(xilinx_path, "Vivado")
    if not os.path.exists(vivado_path):
        logger.error(f"{xilinx_path} does not contain a 'Vivado' directory")
        return ReturnValue.SONAR_NONEXISTENT_PATH

    vivado_versions = os.listdir(vivado_path)
    for version in vivado_versions:
        for tool in ["cad_tool", "sim_tool", "hls_tool"]:
            args = database.DotDict(
                {
                    "type": tool,
                    "ID": f"vivado_{version}",
                    "executable": "vivado",
                    "version": version,
                    "script": f"source setup_vivado.sh {xilinx_path} {version}",
                }
            )
            handler_tool_add(args)
        args = database.DotDict(
            {
                "sim_tool": f"vivado_{version}",
                "hls_tool": f"vivado_{version}",
                "cad_tool": f"vivado_{version}",
                "name": f"vivado_{version}",
            }
        )
        handler_env_add(args)
