import logging
import logging.config
import os
import shutil
from pathlib import Path
import pprint
import sys
import dbm
import shelve
import toml
import textwrap

from sonar.database import Database, DotDict
import sonar.include
from sonar.include import Constants
from sonar.exceptions import ReturnValue, SonarException
from sonar.make import MakeFile

logger = logging.getLogger(__name__)


def activate(args):
    if args.env is not None:
        Env.activate(args)
    else:
        raise NotImplementedError


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

    def f_list(args):
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

    def f_list(args):
        tools = Database.Tool.get()
        pprint.pprint(tools)

    def clear(args):
        Database.Tool.clear()


class Board:
    def add(args):
        Database.Board.add(args)

    def remove(args):
        Database.Board.remove(args)

    def show(args):
        board = Database.Board.get(args)
        pprint.pprint(board)

    def clear(args):
        Database.Board.clear()

    def activate(args):
        Database.Board.activate(args)

    def deactivate(args):
        Database.Board.deactivate()

    def f_list(args):
        active_board = Database.Board.get_active()
        print(f"Active board: {active_board}")
        print("Available boards:")

        boards = Database.Board.get()
        for board in boards:
            print("  " + board)


class Init:
    def one_time_setup(args):
        os.makedirs(Constants.SONAR_PATH, exist_ok=True)

        src_dir = os.path.join(os.path.dirname(__file__), "files_to_copy/home/shell")
        dst_dir = os.path.join(Constants.SONAR_PATH, "shell")
        shutil.copytree(src_dir, dst_dir)
        Database.init()

        with open(Path.home().joinpath(".bashrc"), "r+") as f:
            for line in f:
                if "# added by sonar" in line:
                    break
            else:  # not found, we are at the eof
                f.write(f"source {Constants.SONAR_SHELL_MAIN_SOURCE} # added by sonar")
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

        vivado_script = Constants.SONAR_SHELL_PATH.joinpath("setup_vivado.sh")
        for version in vivado_versions:
            if float(version) <= 2017.2:
                include_dir = os.path.join(xilinx_path, f"Vivado_HLS/{version}/include")
            else:
                include_dir = os.path.join(xilinx_path, f"Vivado/{version}/include")
            args = DotDict(
                {
                    "type": "vivado",
                    # "ID": f"vivado_{version}",
                    "cad_executable": "vivado",
                    "sim_executable": "vivado",
                    "hls_executable": "vivado_hls",
                    "version": version,
                    "hls_include": include_dir,
                    "script": textwrap.dedent(
                        f"""\
                        source {vivado_script} {xilinx_path} {version}
                        export SONAR_CAD_TOOL=vivado
                        export SONAR_CAD_VERSION={version}
                        export SONAR_HLS_TOOL=vivado_hls
                        export SONAR_HLS_VERSION={version}
                        export SONAR_HLS_INCLUDE={include_dir}
                        """
                    ),
                }
            )
            Tool.add(args)
            args = DotDict(
                {
                    "sim_tool": f"vivado:{version}",
                    "hls_tool": f"vivado:{version}",
                    "cad_tool": f"vivado:{version}",
                    "repo": None,
                    "board": None,
                    "name": f"vivado_{version}",
                }
            )
            Env.add(args)


class Repo:
    def add(args):
        Database.Repo.add(args)

    def f_list(args):
        repo = Database.Repo.get()
        pprint.pprint(repo)

    def clear(args):
        Database.Repo.clear()

    def activate(args):
        Database.Repo.activate(args)


class Create:
    def ip(args):
        curr_dir = Path(os.getcwd())

        ip_dir = curr_dir.joinpath(args.name)
        ip_dir.mkdir()

        ip_dir.joinpath("build/bin").mkdir(parents=True)
        ip_dir.joinpath("include").mkdir()
        ip_dir.joinpath("src").mkdir()
        ip_dir.joinpath("testbench").mkdir()
        ip_dir.joinpath("cad").mkdir()
        ip_dir.joinpath("hls").mkdir()

        with open(ip_dir.joinpath(Constants.SONAR_IP_MAKEFILE), "w") as f:
            ip_makefile = MakeFile()
            ip_makefile.add_ip_variables(str(ip_dir))
            f.write(str(ip_makefile))

        src_dir = os.path.join(os.path.dirname(__file__), "files_to_copy/repo/ip")
        shutil.copy(os.path.join(src_dir, "generate_cad.tcl"), ip_dir.joinpath("cad"))
        shutil.copy(os.path.join(src_dir, "generate_hls.tcl"), ip_dir.joinpath("hls"))
        shutil.copy(os.path.join(src_dir, "generate_hls.sh"), ip_dir.joinpath("hls"))

        sonar.include.replace_in_file(
            str(ip_dir.joinpath("cad").joinpath("generate_cad.tcl")),
            "BASE_PATH",
            str(ip_dir),
        )
        sonar.include.replace_in_file(
            str(ip_dir.joinpath("hls").joinpath("generate_hls.tcl")),
            "BASE_PATH",
            str(ip_dir),
        )
        sonar.include.replace_in_file(
            str(ip_dir.joinpath("hls").joinpath("generate_hls.sh")),
            "BASE_PATH",
            str(ip_dir),
        )

        active_repo = Database.Repo.get_active()
        args_2 = DotDict({"name": args.name, "repo": active_repo})
        Database.IP.add_new(args_2)
        repos = Database.Repo.get()
        path = repos[active_repo]["path"]
        init_toml = os.path.join(path, ".sonar", Constants.SONAR_CONFIG_FILE)
        init = toml.load(init_toml)
        init["project"]["ips"] = [args.name]
        print(init)
        with open(init_toml, "w") as f:
            toml.dump(init, f)

    def repo(args):
        curr_dir = Path(os.getcwd())

        ip_dir = curr_dir.joinpath(args.name)
        ip_dir.mkdir()

        src_dir = os.path.join(os.path.dirname(__file__), "files_to_copy/repo/.sonar")
        sonar_dir = ip_dir.joinpath(".sonar")
        shutil.copytree(
            src_dir, sonar_dir, ignore=shutil.ignore_patterns("__pycache__*")
        )

        init_toml = sonar_dir.joinpath(Constants.SONAR_CONFIG_FILE)
        init = toml.load(init_toml)
        init["project"]["name"] = args.name
        with open(init_toml, "w") as f:
            toml.dump(init, f)

        os.chdir(ip_dir)
        args = DotDict({"name": args.name})
        Repo.add(args)
        os.chdir(curr_dir)


class IP:
    class Add:
        def src(args):
            pass


class DB:
    def f_list(args):
        sonar.database.print_db()


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


def check_database():
    try:
        db = shelve.open(Constants.SONAR_DB_PATH, "r")
    except dbm.error:
        Init.one_time_setup(None)
    else:
        db.close()
