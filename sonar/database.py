import textwrap
import pprint
import shelve
import logging
import os
import toml
import runpy

from sonar.include import Constants
from sonar.exceptions import SonarInvalidArgError, SonarInvalidOpError

logger = logging.getLogger(__name__)


class Database:
    @staticmethod
    def init():
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            db["active"] = {}
        Database.Tool.clear()
        Database.Env.clear()
        Database.Board.clear()
        Database.Repo.clear()

    class Tool:
        @staticmethod
        def add(args):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                tools = db["tool"]
                try:
                    _dict = tools[args.type]
                except KeyError:
                    _dict = {"versions": [], "executable": {}, "script": {}}
                if args.version in _dict["versions"]:
                    logger.error(
                        f"{args.version} already exists. Use 'edit' to modify existing tools"
                    )
                    raise SonarInvalidOpError
                _dict["versions"].append(args.version)
                _dict["executable"]["cad"] = args.cad_executable
                _dict["executable"]["hls"] = args.hls_executable
                _dict["executable"]["sim"] = args.sim_executable
                _dict["script"][args.version] = args.script
                tools[args.type] = _dict
                db["tool"] = tools

        # @staticmethod
        # def edit(args):
        #     with shelve.open(Constants.SONAR_DB_PATH) as db:
        #         tools = db["tool"]
        #         try:
        #             _dict = tools[args.type]
        #         except KeyError as exc:
        #             raise SonarInvalidArgError(
        #                 f"{args.type} is not a valid type. Valid types: "
        #                 + str(vars(DBtools()))
        #             ) from exc
        #         value = DBtool(args.executable, args.version, args.script)
        #         _dict[args.ID] = value
        #         tools[args.type] = _dict
        #         db["tool"] = tools

        # @staticmethod
        # def remove(args):
        #     with shelve.open(Constants.SONAR_DB_PATH) as db:
        #         tools = db["tool"]
        #         try:
        #             _dict = tools[args.type]
        #         except KeyError as exc:
        #             raise SonarInvalidArgError(
        #                 f"{args.type} is not a valid type. Valid types: "
        #                 + str(vars(DBtools()))
        #             ) from exc
        #         del _dict[args.ID]
        #         db["tool"] = tools

        @staticmethod
        def get():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                tools = db["tool"]
            return tools

        @staticmethod
        def clear():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                db["tool"] = {}

    class Env:
        @staticmethod
        def add(args):
            elements = []
            for tool in ["cad_tool", "sim_tool", "hls_tool"]:
                split = getattr(args, tool).split(":")
                if len(split) == 2 and split[1] != "":
                    elements.append(tuple(split))
                else:
                    raise SonarInvalidArgError
            elements.append(args.board)
            elements.append(args.repo)
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                env = db["env"]
                env[args.name] = DBenvironment(*elements)
                db["env"] = env

        # @staticmethod
        # def edit(args):
        #     with shelve.open(Constants.SONAR_DB_PATH) as db:
        #         env = db["env"]
        #         env[args.name] = DBenvironment(
        #             args.cad_tool, args.sim_tool, args.hls_tool, args.repo, args.board
        #         )
        #         db["env"] = env

        # @staticmethod
        # def remove(args):
        #     with shelve.open(Constants.SONAR_DB_PATH) as db:
        #         env = db["env"]
        #         del env[args.name]
        #         db["env"] = env

        @staticmethod
        def get():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                env = db["env"]
            return env

        @staticmethod
        def clear():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                db["env"] = {}

        @staticmethod
        def activate(args):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                try:
                    env = db["env"][args.env]
                except KeyError as exc:
                    logger.error(
                        f"Could not find environment: {args.env}. See envs with `sonar env show`"
                    )
                    raise SonarInvalidArgError from exc
                with open(Constants.SONAR_SHELL_TOOL_SOURCE, "w") as f:
                    script = []
                    for key in ["cad_tool", "sim_tool", "hls_tool"]:
                        tool_id = env[key]
                        tool_script = db["tool"][tool_id[0]]["script"][tool_id[1]]
                        if tool_script not in script:
                            script.append(tool_script)
                    f.write("\n".join(script))

    class Board:
        @staticmethod
        def add(args):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                boards = db["board"]
                board_name = os.path.basename(args.path)
                boards[board_name] = args.path
                db["board"] = boards

        @staticmethod
        def remove(args):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                boards = db["board"]
                del boards[args.name]
                db["board"] = boards

        @staticmethod
        def clear():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                db["board"] = {}
                dict_active = db["active"]
                dict_active["board"] = None
                db["active"] = dict_active

        @staticmethod
        def get(args=None):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                boards = db["board"]
                if args:
                    return boards[args.name]
                return boards

        @staticmethod
        def activate(args):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                try:
                    board = db["board"][args.board]
                except KeyError as exc:
                    logger.error(
                        f"Could not find board: {args.board}. See boards with `sonar board info`"
                    )
                    raise SonarInvalidArgError from exc
                with open(Constants.SONAR_SHELL_BOARD_SOURCE, "w") as f:
                    script = []
                    board_settings = runpy.run_path(os.path.join(board, "__init__.py"))
                    part = board_settings["PART"]
                    script.append(f"export SONAR_BOARD={args.board}")
                    script.append(f"export SONAR_PART={part}")
                    part_family = Database.Board._find_part_family(part)
                    if part_family:
                        script.append(f"export SONAR_PART_FAMILY={part_family}")
                    f.write("\n".join(script))
                dict_active = db["active"]
                dict_active["board"] = args.board
                db["active"] = dict_active

        @staticmethod
        def deactivate():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                os.remove(Constants.SONAR_SHELL_BOARD_SOURCE)
                dict_active = db["active"]
                dict_active["board"] = None
                db["active"] = dict_active

        @staticmethod
        def get_active():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                return db["active"]["board"]

        @staticmethod
        def _find_part_family(fpga_part):
            family_id = fpga_part[2]
            if family_id == "k":
                family = "Kintex"
            elif family_id == "v":
                family = "Virtex"
            elif family_id == "7":
                family = "7series"
            else:
                family_id = fpga_part[2:4]
                if family_id == "zu":
                    return "Zynq_Ultrascale_Plus"
                return None

            if family == "7series":
                fpga_type_id = fpga_part[3]
                if fpga_type_id == "k":
                    fpga_type = "Kintex"
                elif fpga_type_id == "v":
                    fpga_type = "Virtex"
                elif fpga_type_id == "z":
                    fpga_type = "Zynq"
                else:
                    return None
            else:
                fpga_type_id = fpga_part.split("-")[0][-1]
                if fpga_type_id == "p":
                    fpga_type = "Ultrascale_Plus"
                else:
                    fpga_type = "Ultrascale"

            return f"{family}_{fpga_type}"

    class Repo:
        @staticmethod
        def add(args):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                repos = db["repo"]
                repo_path = os.getcwd()
                config = toml.load(
                    os.path.join(repo_path, Constants.SONAR_CONFIG_FILE_PATH)
                )
                repo = config["project"]["name"]
                repos[repo] = {"path": repo_path}
                db["repo"] = repos

        @staticmethod
        def clear():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                db["repo"] = {}
                dict_active = db["active"]
                dict_active["repo"] = None
                db["active"] = dict_active

        @staticmethod
        def get():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                repos = db["repo"]
            return repos

        @staticmethod
        def activate(args):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                try:
                    env = db["repo"][args.repo]
                except KeyError as exc:
                    logger.error(
                        f"Could not find repo: {args.repo}. See repos with `sonar repo show`"
                    )
                    raise SonarInvalidArgError from exc
                with open(Constants.SONAR_SHELL_REPO_SOURCE, "w") as f:
                    script = []
                    path = env["path"]
                    script.append(f"export SONAR_REPO={path}\n")
                    f.write("\n".join(script))
                dict_active = db["active"]
                dict_active["repo"] = args.repo
                db["active"] = dict_active

        @staticmethod
        def deactivate():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                os.remove(Constants.SONAR_SHELL_REPO_SOURCE)
                dict_active = db["active"]
                dict_active["repo"] = None
                db["active"] = dict_active

        @staticmethod
        def get_active():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                return db["active"]["repo"]

    class IP:
        @staticmethod
        def add_new(args):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                repos = db["repo"]
                repo = repos[args.repo]
                if "ips" not in repo:
                    repo["ips"] = []
                repo["ips"].append({"name": args.name})
                db["repo"] = repos


# https://stackoverflow.com/a/32107024
class DotDict(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)


class SubscriptMixin:
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class DBtools(SubscriptMixin):
    def __init__(self):
        self.cad_tool = {}
        self.sim_tool = {}
        self.hls_tool = {}

    def __repr__(self):
        return f"""\
        {self.cad_tool}
        {self.sim_tool}
        {self.hls_tool}\
        """

    def __str__(self):
        tool_str = ["cad:"]
        tool_str.append(textwrap.indent(pprint.pformat(self.cad_tool), "    "))
        tool_str.append("sim:")
        tool_str.append(textwrap.indent(pprint.pformat(self.sim_tool), "    "))
        tool_str.append("hls:")
        tool_str.append(textwrap.indent(pprint.pformat(self.hls_tool), "    "))
        return "\n".join(tool_str)


class DBenvironment(SubscriptMixin):
    def __init__(self, _cad_tool, _sim_tool, _hls_tool, _board, _project):
        self.cad_tool = _cad_tool
        self.sim_tool = _sim_tool
        self.hls_tool = _hls_tool
        self.board = _board
        self.project = _project

    def __repr__(self):
        env_dict = {
            "cad_tool": {self.cad_tool},
            "sim_tool": {self.sim_tool},
            "hls_tool": {self.hls_tool},
            "board": {self.board},
            "project": {self.project},
        }
        return str(env_dict)

    def __str__(self):
        return textwrap.dedent(
            f"""\
            Environment:
                cad_tool: {self.cad_tool}
                sim_tool: {self.sim_tool}
                hls_tool: {self.hls_tool}
                board: {self.board}
                project: {self.project}\
            """
        )


class DBtool(SubscriptMixin):
    def __init__(self, _name, _version, _script):
        self.name = _name
        self.version = _version
        self.script = _script

    def __repr__(self):
        return f"<database.Tool()>"

    def __str__(self):
        return textwrap.dedent(
            f"""\
            name: {self.name}
            version: {self.version}
            script: {self.script}\
            """
        )


class Repo(SubscriptMixin):
    def __init__(self, _name, _path):
        self.name = _name
        self.path = _path

        self.script = f"export SONAR_REPO_PATH={_path}"

    def __repr__(self):
        return f"<database.Repo()>"

    def __str__(self):
        return textwrap.dedent(
            f"""\
            name: {self.name}
            path: {self.path}
            script: {self.script}\
            """
        )


class Board(SubscriptMixin):
    def __init__(self, _name, _part):
        self.name = _name
        self.part = _part

        self.script = textwrap.dedent(
            f"""\
            export SONAR_BOARD={_name}"
            export SONAR_PART={_part}

        """
        )

    def __repr__(self):
        return f"<database.Board({self.name}, {self.part}, {self.script})>"

    def __str__(self):
        return textwrap.dedent(
            f"""\
            name: {self.name}
            part: {self.part}
            script: {self.script}\
            """
        )


def print_db():
    with shelve.open(Constants.SONAR_DB_PATH, "r") as db:
        dkeys = list(db.keys())
        dkeys.sort()
        for x in dkeys:
            print(x, pprint.pformat(db[x]))
