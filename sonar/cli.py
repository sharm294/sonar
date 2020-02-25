import logging
import os
import shelve
import shutil
import pprint
import sys

from sonar.database import Database, DotDict
from sonar.include import Constants
from sonar.exceptions import ReturnValue, SonarException

logger = logging.getLogger(__name__)


def handle_activate(args):
    with shelve.open(Constants.SONAR_DB_PATH) as db:
        env = db["env"][args.env]
        with open(Constants.SONAR_BASH_ENV_SOURCE, "w") as f:
            script = []
            for key in ["cad_tool", "sim_tool", "hls_tool"]:
                tool_id = env[key]
                tool = db["tool"][key][tool_id]
                if tool.script not in script:
                    script.append(tool.script)
            f.write("\n".join(script))


def handler_tool_add(args):
    try:
        Database.Tool.add(args)
    except SonarException as exc:
        logger.exception(f"Adding a tool to the database failed: {exc.exit_str}")
        sys.exit(exc.exit_code)


def handler_tool_remove(args):
    try:
        Database.Tool.remove(args)
    except SonarException as exc:
        logger.error(f"Removing a tool from the database failed: {exc.exit_str}")
        sys.exit(exc.exit_code)


def handler_tool_edit(args):
    try:
        Database.Tool.edit(args)
    except SonarException as exc:
        logger.error(f"Editing a tool in the database failed: {exc.exit_str}")
        sys.exit(exc.exit_code)


def handler_tool_show(args):
    tools = Database.Tool.get()
    print(tools)


def handler_tool_clear(args):
    Database.Tool.clear()


def handler_env_add(args):
    Database.Env.add(args)


def handler_env_remove(args):
    Database.Env.remove(args)


def handler_env_edit(args):
    Database.Env.edit(args)


def handler_env_show(args):
    env = Database.Env.get()
    pprint.pprint(env)


def handler_env_clear(args):
    Database.Env.clear()


def handle_init(args):
    os.makedirs(Constants.SONAR_PATH, exist_ok=True)

    src_dir = os.path.join(os.path.dirname(__file__), "shell")
    dst_dir = os.path.join(Constants.SONAR_PATH, "shell")
    shutil.copytree(src_dir, dst_dir)
    handler_tool_clear(args)
    handler_env_clear(args)


def handler_init_vivado(args):
    xilinx_path = os.path.abspath(args.path)
    if not os.path.exists(xilinx_path):
        logger.error(f"Path does not exist: {xilinx_path}")
        sys.exit(ReturnValue.SONAR_NONEXISTENT_PATH)

    vivado_path = os.path.join(xilinx_path, "Vivado")
    try:
        vivado_versions = os.listdir(vivado_path)
    except FileNotFoundError:
        logger.error(f"No 'Vivado/' directory found in {xilinx_path}")
        sys.exit(ReturnValue.SONAR_INVALID_PATH)

    for version in vivado_versions:
        for tool in ["cad_tool", "sim_tool", "hls_tool"]:
            args = DotDict(
                {
                    "type": tool,
                    "ID": f"vivado_{version}",
                    "executable": "vivado",
                    "version": version,
                    "script": f"source setup_vivado.sh {xilinx_path} {version}",
                }
            )
            handler_tool_add(args)
        args = DotDict(
            {
                "sim_tool": f"vivado_{version}",
                "hls_tool": f"vivado_{version}",
                "cad_tool": f"vivado_{version}",
                "name": f"vivado_{version}",
            }
        )
        handler_env_add(args)
