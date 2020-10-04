"""
The Sonar API is defined here to interact with the sonar database and perform
the CLI tasks.
"""

import logging
import logging.config
import os
import pprint
import shutil
import sys
import textwrap
from distutils.dir_util import copy_tree
from pathlib import Path

import toml

import sonar.database
from sonar.exceptions import ReturnValue, SonarException
from sonar.include import Constants
from sonar.make import MakeFile

logger = logging.getLogger(__name__)


def activate(args):
    """
    Activate a particular environment by name.

    Args:
        args (object): Holds attributes
            name (str): Name of the enviroment to activate
    """
    if args.name is not None:
        Env.activate(args)
    else:
        logger.error("Activating environment failed: no name specified")


class Env:
    """
    The Env class defines functions to interact with sonar's environments.
    Environments define a particular set of tools, board and repository that
    users can switch between.
    """

    @staticmethod
    def activate(args):
        """
        Activate a particular environment by name.

        Args:
            args (object): Holds attributes
                name (str): Name of the enviroment to activate
        """
        try:
            sonar.database.Env.activate(args.name)
        except SonarException as exc:
            logger.error("Activating environment failed: %s", exc.exit_str)
            sys.exit(exc.exit_code)

    @staticmethod
    def add(args):
        """
        Add a new environment to the database.

        Args:
            args (object): Holds attributes
                cad (str): CAD tool of the form "name:version"
                sim (str): Simulation tool of the form "name:version"
                hls (str): HLS tool of the form "name:version"
                name (str): Name of the environment
                board (str): Name of the board
                repo (str): Name of the repository
        """
        cad_tool = args.cad.split(":")
        sim_tool = args.sim.split(":")
        hls_tool = args.hls.split(":")
        sonar.database.Env.add(
            args.name, cad_tool, hls_tool, sim_tool, args.board, args.repo
        )

    @staticmethod
    def remove(args):
        """
        Remove an environment from the database

        Args:
            args (object): Holds attributes
                name (str): Name of the environment to remove
        """
        sonar.database.Env.remove(args.name)

    @staticmethod
    def f_list(_args):
        """
        List the environments in the database

        Args:
            _args (object): Unused
        """
        env = sonar.database.Env.get()
        pprint.pprint(env)

    @staticmethod
    def clear(_args):
        """
        Clear all environments in the database

        Args:
            _args (object): Unused
        """
        sonar.database.Env.clear()


class Tool:
    """
    The Tool class defines functions to interact with sonar's CAD, HLS and
    simulation tools.
    """

    @staticmethod
    def add(args):
        """
        Add a new tool to the database.

        Args:
            args (object): Holds attributes
                name (str): Name of tool
                version (str): Version of tool
                cad (str): Name of CAD executable
                hls (str): Name of HLS executable
                sim (str): Name of simulation executable
                script (str): Shell script to initialize tool
        """
        try:
            sonar.database.Tool.add(
                args.name, args.version, args.cad, args.hls, args.sim, args.script
            )
        except SonarException as exc:
            logger.exception("Adding a tool to the database failed: %s", exc.exit_str)
            sys.exit(exc.exit_code)

    # def remove(args):
    #     try:
    #         sonar.database.Tool.remove(args)
    #     except SonarException as exc:
    #         logger.error(f"Removing a tool from the database failed: {exc.exit_str}")
    #         sys.exit(exc.exit_code)

    # def edit(args):
    #     try:
    #         sonar.database.Tool.edit(args)
    #     except SonarException as exc:
    #         logger.error(f"Editing a tool in the database failed: {exc.exit_str}")
    #         sys.exit(exc.exit_code)

    @staticmethod
    def f_list(_args):
        """
        List the tools in the sonar database

        Args:
            _args (object): Unused
        """
        tools = sonar.database.Tool.get()
        pprint.pprint(tools)

    @staticmethod
    def clear(_args):
        """
        Clear the database of tools

        Args:
            _args (object): Unused
        """
        sonar.database.Tool.clear()


class Board:
    """
    The Board class defines functions to interact with sonar's list of hardware
    boards.
    """

    @staticmethod
    def add(args):
        """
        Add a new board to sonar database

        Args:
            args (object): Holds attributes
                path (str): Path to the board definition
        """
        sonar.database.Board.add(args.path)

    @staticmethod
    def remove(args):
        """
        Remove a board from the sonar database

        Args:
            args (object): Holds attributes
                name (str): Name of board to remove
        """
        sonar.database.Board.remove(args.name)

    @staticmethod
    def show(args):
        """
        Print a particular board by name

        Args:
            args (object): Holds attributes
                name (str): Name of board to show
        """
        board = sonar.database.Board.get(args.name)
        pprint.pprint(board)

    @staticmethod
    def clear(_args):
        """
        Remove all boards from the sonar database

        Args:
            _args (object): Unused
        """
        sonar.database.Board.clear()

    @staticmethod
    def activate(args):
        """
        Activate a board by name

        Args:
            args (object): Holds attributes
                name (str): Name of board to activate
        """
        sonar.database.Board.activate(args.name)

    @staticmethod
    def deactivate(_args):
        """
        Deactivate the active board

        Args:
            _args (object): Unused
        """
        sonar.database.Board.deactivate()

    @staticmethod
    def f_list(_args):
        """
        List the active board and all boards in the sonar database

        Args:
            _args (object): Holds attributes
        """
        active_board = sonar.database.Board.get_active()
        print(f"Active board: {active_board}")
        print("Available boards:")

        boards = sonar.database.Board.get()
        for board in boards:
            print("  " + board)


class Init:
    """
    The Init class defines functions to initialize sonar in various ways.
    """

    @staticmethod
    def one_time_setup(_args):
        """
        Performs initial setup for sonar. It creates the database, copies files
        over to the user sonar directory and adds the default boards to the
        database.

        Args:
            _args (object): Unused
        """
        sonar.database.init()

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
        boards = [x for x in files if x not in ("__init__.py", "__pycache__")]
        for board in boards:
            path = os.path.join(os.path.dirname(__file__), "boards", board)
            sonar.database.Board.add(path)

    @staticmethod
    def vivado(args):
        """
        Helper function to initialize Xilinx tools

        Args:
            args (object): Holds attributes
                path (str): Path to the Xilinx directory containing Vivado
        """
        xilinx_path = os.path.abspath(args.path)
        if not os.path.exists(xilinx_path):
            logger.error("Path does not exist: %s", xilinx_path)
            sys.exit(ReturnValue.SONAR_NONEXISTENT_PATH)

        vivado_path = os.path.join(xilinx_path, "Vivado")
        try:
            vivado_versions = os.listdir(vivado_path)
        except FileNotFoundError:
            logger.error("No 'Vivado/' directory found in %s", xilinx_path)
            sys.exit(ReturnValue.SONAR_INVALID_PATH)

        vivado_script = Constants.SONAR_SHELL_PATH.joinpath("setup_vivado.sh")
        for version in vivado_versions:
            if float(version) <= 2017.2:
                include_dir = os.path.join(xilinx_path, f"Vivado_HLS/{version}/include")
            else:
                include_dir = os.path.join(xilinx_path, f"Vivado/{version}/include")
            args = sonar.include.DotDict(
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
            args = sonar.include.DotDict(
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
    """
    The Repo class defines functions to interact with sonar's repositories.
    """

    @staticmethod
    def add(_args):
        """
        Add a new repository to the database

        Args:
            _args (object): Unused
        """
        sonar.database.Repo.add()

    @staticmethod
    def f_list(_args):
        """
        List all the repositories in the database

        Args:
            _args (object): Unused
        """
        repo = sonar.database.Repo.get()
        pprint.pprint(repo)

    @staticmethod
    def clear(_args):
        """
        Clear the list of repositories in the database

        Args:
            _args (object): Unused
        """
        # TODO accept an argument to remove a particular one
        sonar.database.Repo.clear()

    @staticmethod
    def activate(args):
        """
        Activate a particular repository

        Args:
            args (object): Should have "name" attribute
        """
        sonar.database.Repo.activate(args.name)


class Create:
    """
    The Create class defines functions to create new IPs and repos in sonar.
    """

    @staticmethod
    def ip(args):
        """
        Create a new sonar IP in the current working directory.

        Args:
            args (object): Should have "name" attribute
        """
        curr_dir = Path(os.getcwd())

        ip_dir = curr_dir.joinpath(args.name)
        ip_dir.mkdir()

        ip_dir.joinpath("build/bin").mkdir(parents=True)
        ip_dir.joinpath("include").mkdir()
        ip_dir.joinpath("src").mkdir()
        ip_dir.joinpath("testbench/build/bin").mkdir(parents=True)
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

        sonar.include.replace_in_file(
            str(ip_dir.joinpath("cad").joinpath("generate_cad.tcl")),
            "BASE_PATH",
            base_ip_path_tcl,
        )
        sonar.include.replace_in_file(
            str(ip_dir.joinpath("cad").joinpath("generate_cad.sh")),
            "BASE_PATH",
            base_ip_path_sh,
        )
        sonar.include.replace_in_file(
            str(ip_dir.joinpath("hls").joinpath("generate_hls.tcl")),
            "BASE_PATH",
            base_ip_path_tcl,
        )
        sonar.include.replace_in_file(
            str(ip_dir.joinpath("hls").joinpath("generate_hls.sh")),
            "BASE_PATH",
            base_ip_path_sh,
        )
        sonar.include.replace_in_file(
            str(ip_dir.joinpath("run.sh")),
            "BASE_PATH",
            base_ip_path_sh,
        )

        # active_repo = sonar.database.Repo.get_active()
        sonar.database.IP.add_new(args.name, ip_dir)
        # repos = sonar.database.Repo.get()
        # path = repos[active_repo]["path"]
        # init_toml = os.path.join(path, Constants.SONAR_CONFIG_FILE)
        # init = toml.load(init_toml)
        # init["project"]["ips"] = [args.name]
        # print(init)
        # with open(init_toml, "w") as f:
        #     toml.dump(init, f)

    @staticmethod
    def repo(args):
        """
        Create a new sonar repo in the current working directory.

        Args:
            args (object): Should have "name" attribute
        """
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
        args = sonar.include.DotDict({"name": args.name})
        Repo.add(args)
        os.chdir(curr_dir)


# class IP:
#     class Add:
#         def src(args):
#             current_path = os.getcwd()
#             # active_repo = sonar.database.Repo.get_active()
#             # repo = sonar.database.Repo.get(active_repo)
#             sonar.database.IP.add_src(args.name, current_path, args.type)


class Database:
    """
    The Database class defines functions to interact with sonar's sonar database.
    """

    @staticmethod
    def f_list(_args=None):
        """
        Print the database to stdout.

        Args:
            _args (object): unused
        """
        sonar.database.print_db()


def configure_logging():
    """
    Defines a standard set of logging practices across sonar
    """
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
    """
    Checks to see if the sonar database exists. If it does not, performs the
    setup to initialize the database.
    """
    if not sonar.database.check_database():
        Init.one_time_setup(None)
