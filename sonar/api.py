from distutils.dir_util import copy_tree
import logging
import logging.config
import os
import shutil
from pathlib import Path
import pprint
import sys
import toml
import textwrap

import sonar.database as Database
import sonar.utils
from sonar.include import Constants
from sonar.exceptions import ReturnValue, SonarException
from sonar.make import MakeFile

logger = logging.getLogger(__name__)


def activate(args):
    if args.name is not None:
        Env.activate(args)
    else:
        raise NotImplementedError


class Env:
    @staticmethod
    def activate(args):
        try:
            Database.Env.activate(args.name)
        except SonarException as exc:
            logger.error(f"Activating environment failed: {exc.exit_str}")
            sys.exit(exc.exit_code)

    @staticmethod
    def add(args):
        cad_tool = args.cad.split(":")
        sim_tool = args.sim.split(":")
        hls_tool = args.hls.split(":")
        Database.Env.add(args.name, cad_tool, hls_tool, sim_tool, args.board, args.repo)

    @staticmethod
    def remove(args):
        Database.Env.remove(args.name)

    @staticmethod
    def f_list(args):
        env = Database.Env.get()
        pprint.pprint(env)

    @staticmethod
    def clear(args):
        Database.Env.clear()


class Tool:
    @staticmethod
    def add(args):
        try:
            Database.Tool.add(
                args.type, args.version, args.cad, args.hls, args.sim, args.script
            )
        except SonarException as exc:
            logger.exception(f"Adding a tool to the database failed: {exc.exit_str}")
            sys.exit(exc.exit_code)

    # def remove(args):
    #     try:
    #         Database.Tool.remove(args)
    #     except SonarException as exc:
    #         logger.error(f"Removing a tool from the database failed: {exc.exit_str}")
    #         sys.exit(exc.exit_code)

    # def edit(args):
    #     try:
    #         Database.Tool.edit(args)
    #     except SonarException as exc:
    #         logger.error(f"Editing a tool in the database failed: {exc.exit_str}")
    #         sys.exit(exc.exit_code)

    @staticmethod
    def f_list(args):
        tools = Database.Tool.get()
        pprint.pprint(tools)

    @staticmethod
    def clear():
        Database.Tool.clear()


class Board:
    @staticmethod
    def add(args):
        Database.Board.add(args.path)

    @staticmethod
    def remove(args):
        Database.Board.remove(args.name)

    @staticmethod
    def show(args):
        board = Database.Board.get(args.name)
        pprint.pprint(board)

    @staticmethod
    def clear(args):
        Database.Board.clear()

    @staticmethod
    def activate(args):
        Database.Board.activate(args.name)

    @staticmethod
    def deactivate(args):
        Database.Board.deactivate()

    @staticmethod
    def f_list(args):
        active_board = Database.Board.get_active()
        print(f"Active board: {active_board}")
        print("Available boards:")

        boards = Database.Board.get()
        for board in boards:
            print("  " + board)


class Init:
    @staticmethod
    def one_time_setup(args):
        Database.init()

        src_dir = os.path.join(os.path.dirname(__file__), "files_to_copy/home")
        # dst_dir = os.path.join(Constants.SONAR_PATH)
        # need to use this copy tree instead of shutil because shutil copytree
        # expects the dst directory doesn't exist
        copy_tree(src_dir, str(Constants.SONAR_PATH))

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
            Database.Board.add(path)

    @staticmethod
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
            args = sonar.utils.DotDict(
                {
                    "type": "vivado",
                    # "ID": f"vivado_{version}",
                    "cad": "vivado",
                    "sim": "vivado",
                    "hls": "vivado_hls",
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
            args = sonar.utils.DotDict(
                {
                    "sim": f"vivado:{version}",
                    "hls": f"vivado:{version}",
                    "cad": f"vivado:{version}",
                    "repo": None,
                    "board": None,
                    "name": f"vivado_{version}",
                }
            )
            Env.add(args)


class Repo:
    @staticmethod
    def add(args):
        Database.Repo.add()

    @staticmethod
    def f_list(args):
        repo = Database.Repo.get()
        pprint.pprint(repo)

    @staticmethod
    def clear(args):
        Database.Repo.clear()

    @staticmethod
    def activate(args):
        Database.Repo.activate(args.name)


class Create:
    @staticmethod
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
            # ip_makefile.add_ip_variables(str(ip_dir))
            f.write(str(ip_makefile.ip(str(ip_dir))))

        with open(ip_dir.joinpath("Makefile"), "w") as f:
            f.write("include sonar.mk")

        src_dir = os.path.join(os.path.dirname(__file__), "files_to_copy/repo/ip")
        shutil.copy(os.path.join(src_dir, "generate_cad.tcl"), ip_dir.joinpath("cad"))
        shutil.copy(os.path.join(src_dir, "generate_cad.sh"), ip_dir.joinpath("cad"))
        shutil.copy(os.path.join(src_dir, "generate_hls.tcl"), ip_dir.joinpath("hls"))
        shutil.copy(os.path.join(src_dir, "generate_hls.sh"), ip_dir.joinpath("hls"))
        shutil.copy(os.path.join(src_dir, "run.sh"), ip_dir)

        base_ip_path_sh = str(ip_dir).replace(os.getenv("SONAR_REPO"), "$SONAR_REPO")
        base_ip_path_tcl = str(ip_dir).replace(
            os.getenv("SONAR_REPO"), "${::env(SONAR_REPO)}"
        )

        sonar.utils.replace_in_file(
            str(ip_dir.joinpath("cad").joinpath("generate_cad.tcl")),
            "BASE_PATH",
            base_ip_path_tcl,
        )
        sonar.utils.replace_in_file(
            str(ip_dir.joinpath("cad").joinpath("generate_cad.sh")),
            "BASE_PATH",
            base_ip_path_sh,
        )
        sonar.utils.replace_in_file(
            str(ip_dir.joinpath("hls").joinpath("generate_hls.tcl")),
            "BASE_PATH",
            base_ip_path_tcl,
        )
        sonar.utils.replace_in_file(
            str(ip_dir.joinpath("hls").joinpath("generate_hls.sh")),
            "BASE_PATH",
            base_ip_path_sh,
        )
        sonar.utils.replace_in_file(
            str(ip_dir.joinpath("run.sh")), "BASE_PATH", base_ip_path_sh,
        )

        # active_repo = Database.Repo.get_active()
        Database.IP.add_new(args.name, ip_dir)
        # repos = Database.Repo.get()
        # path = repos[active_repo]["path"]
        # init_toml = os.path.join(path, Constants.SONAR_CONFIG_FILE)
        # init = toml.load(init_toml)
        # init["project"]["ips"] = [args.name]
        # print(init)
        # with open(init_toml, "w") as f:
        #     toml.dump(init, f)

    @staticmethod
    def repo(args):
        curr_dir = Path(os.getcwd())

        repo_dir = curr_dir.joinpath(args.name)
        repo_dir.mkdir()

        src_dir = os.path.join(os.path.dirname(__file__), "files_to_copy/repo/.sonar")
        sonar_dir = repo_dir.joinpath(".sonar")
        shutil.copytree(
            src_dir, sonar_dir, ignore=shutil.ignore_patterns("__pycache__*")
        )

        src_file = os.path.join(
            os.path.dirname(__file__), "files_to_copy/repo/.gitignore"
        )
        shutil.copy(src_file, repo_dir)

        init_toml = repo_dir.joinpath(Constants.SONAR_CONFIG_FILE_PATH)
        init = toml.load(init_toml)
        init["project"]["name"] = args.name
        with open(init_toml, "w") as f:
            toml.dump(init, f)

        os.chdir(repo_dir)
        args = sonar.utils.DotDict({"name": args.name})
        Repo.add(args)
        os.chdir(curr_dir)


# class IP:
#     class Add:
#         def src(args):
#             current_path = os.getcwd()
#             # active_repo = Database.Repo.get_active()
#             # repo = Database.Repo.get(active_repo)
#             Database.IP.add_src(args.name, current_path, args.type)


class DB:
    @staticmethod
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
    if not Database.check_database():
        Init.one_time_setup(None)
