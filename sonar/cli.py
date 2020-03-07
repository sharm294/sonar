import logging
import os
import shutil
from pathlib import Path
import pprint
import sys

from sonar.database import Database, DotDict
from sonar.include import Constants
from sonar.exceptions import ReturnValue, SonarException

logger = logging.getLogger(__name__)


class Env:
    def activate(args):
        try:
            Database.Env.activate(args)
        except SonarException as exc:
            logger.error(f"Activating environment failed: {exc.exit_str}")
            sys.exit(exc.exit_code)

    def add(args):
        Database.Env.add(args)

    def remove(args):
        Database.Env.remove(args)

    def edit(args):
        Database.Env.edit(args)

    def show(args):
        env = Database.Env.get()
        pprint.pprint(env)

    def clear(args):
        Database.Env.clear()


class Tool:
    def add(args):
        try:
            Database.Tool.add(args)
        except SonarException as exc:
            logger.exception(f"Adding a tool to the database failed: {exc.exit_str}")
            sys.exit(exc.exit_code)

    def remove(args):
        try:
            Database.Tool.remove(args)
        except SonarException as exc:
            logger.error(f"Removing a tool from the database failed: {exc.exit_str}")
            sys.exit(exc.exit_code)

    def edit(args):
        try:
            Database.Tool.edit(args)
        except SonarException as exc:
            logger.error(f"Editing a tool in the database failed: {exc.exit_str}")
            sys.exit(exc.exit_code)

    def show(args):
        tools = Database.Tool.get()
        pprint.pprint(tools)

    def clear(args):
        Database.Tool.clear()


class Board:
    def add(args):
        Database.Board.add(args)

    def show(args):
        board = Database.Board.get()
        pprint.pprint(board)

    def clear(args):
        Database.Board.clear()

    def activate(args):
        Database.Board.activate(args)


class Init:
    def one_time_setup(args):
        os.makedirs(Constants.SONAR_PATH, exist_ok=True)

        src_dir = os.path.join(os.path.dirname(__file__), "shell")
        dst_dir = os.path.join(Constants.SONAR_PATH, "shell")
        shutil.copytree(src_dir, dst_dir)
        Tool.clear(args)
        Env.clear(args)
        Database.Board.clear()
        Database.Repo.clear()
        with open(Path.home().joinpath(".bashrc"), "r+") as f:
            for line in f:
                if "# added by sonar" in line:
                    break
            else:  # not found, we are at the eof
                f.write(f"source {Constants.SONAR_BASH_MAIN_SOURCE} # added by sonar")
        files = os.listdir(os.path.join(os.path.dirname(__file__), "boards"))
        boards = [x for x in files if x != "__init__.py" and x != "__pycache__"]
        for board in boards:
            path = os.path.join(os.path.dirname(__file__), "boards", board)
            args = DotDict({"path": path})
            Database.Board.add(args)

    def vivado(args):
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

        vivado_script = Constants.SONAR_BASH_PATH.joinpath("setup_vivado.sh")
        for version in vivado_versions:
            # for tool in ["cad_tool", "sim_tool", "hls_tool"]:
            args = DotDict(
                {
                    "type": "vivado",
                    # "ID": f"vivado_{version}",
                    "cad_executable": "vivado",
                    "sim_executable": "vivado",
                    "hls_executable": "vivado_hls",
                    "version": version,
                    "script": f"source {vivado_script} {xilinx_path} {version}",
                }
            )
            Tool.add(args)
            args = DotDict(
                {
                    "sim_tool": ("vivado", version),
                    "hls_tool": ("vivado", version),
                    "cad_tool": ("vivado", version),
                    "name": f"vivado_{version}",
                }
            )
            Env.add(args)

    def repo(args):
        os.makedirs()


class Repo:
    def add(args):
        Database.Repo.add(args)

    def show(args):
        repo = Database.Repo.get()
        pprint.pprint(repo)

    def clear(args):
        Database.Repo.clear()

    def activate(args):
        Database.Repo.activate(args)


class Project:
    def add(args):
        curr_dir = Path(os.getcwd())

        ip_dir = curr_dir.joinpath(args.name)
        ip_dir.mkdir()

        ip_dir.joinpath("build/bin").mkdir(parents=True)
        ip_dir.joinpath("include").mkdir()
        ip_dir.joinpath("src").mkdir()
        ip_dir.joinpath("testbench").mkdir()
        ip_dir.joinpath("cad").mkdir()
        ip_dir.joinpath("hls").mkdir()
