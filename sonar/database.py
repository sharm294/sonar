import pprint
import shelve
import dbm
import logging
import os
import toml
import runpy

from sonar.include import Constants
from sonar.exceptions import SonarInvalidArgError, SonarInvalidOpError

logger = logging.getLogger(__name__)


def init():
    os.makedirs(Constants.SONAR_PATH, exist_ok=True)
    with shelve.open(Constants.SONAR_DB_PATH) as db:
        db["active"] = {
            "cad": None,
            "hls": None,
            "sim": None,
            "board": None,
            "repo": None,
        }
    Tool.clear()
    Env.clear()
    Board.clear()
    Repo.clear()


class Tool:
    @staticmethod
    def add(tool_name, version, cad_exe, hls_exe, sim_exe, script):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            tools = db["tool"]
            try:
                _dict = tools[tool_name]
            except KeyError:
                _dict = {"versions": [], "executable": {}, "script": {}}
            if version in _dict["versions"]:
                logger.error(
                    f"{version} already exists. Use 'edit' to modify existing tools"
                )
                raise SonarInvalidOpError
            _dict["versions"].append(version)
            _dict["executable"]["cad"] = cad_exe
            _dict["executable"]["hls"] = hls_exe
            _dict["executable"]["sim"] = sim_exe
            _dict["script"][version] = script
            tools[tool_name] = _dict
            db["tool"] = tools

    @staticmethod
    def get(tool=None):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            tools = db["tool"]
        if tool is None:
            return tools
        if tool not in tools:
            raise SonarInvalidArgError
        return tools[tool]

    @staticmethod
    def get_active():
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            active = db["active"]
            return {k: active[k] for k in ("cad", "hls", "sim")}

    @staticmethod
    def clear():
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            db["tool"] = {}
            active = db["active"]
            for key in ("cad", "hls", "sim"):
                active[key] = None
            db["active"] = active

    @staticmethod
    def activate(cad_tool, hls_tool, sim_tool):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            active = db["active"]
            active["cad"] = cad_tool
            active["hls"] = hls_tool
            active["sim"] = sim_tool

            tools = db["tool"]
            with open(Constants.SONAR_SHELL_TOOL_SOURCE, "w") as f:
                script = []
                for key in ["cad", "sim", "hls"]:
                    tool = active[key]
                    if tool:
                        tool_id, version = tool
                        tool_script = tools[tool_id]["script"][version]
                        if tool_script not in script:
                            script.append(tool_script)
                f.write("\n".join(script))
            db["active"] = active

    @staticmethod
    def deactivate():
        if os.path.exists(Constants.SONAR_SHELL_TOOL_SOURCE):
            os.remove(Constants.SONAR_SHELL_TOOL_SOURCE)
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            active = db["active"]
            active["cad"] = None
            active["hls"] = None
            active["sim"] = None
            db["active"] = active


class Env:
    @staticmethod
    def add(name, cad_tool, hls_tool, sim_tool, board, repo):
        _dict = {}
        _dict["cad"] = cad_tool
        _dict["hls"] = hls_tool
        _dict["sim"] = sim_tool
        _dict["board"] = board
        _dict["repo"] = repo
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            env = db["env"]
            env[name] = _dict
            db["env"] = env

    @staticmethod
    def get(name=None):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            envs = db["env"]
            if name is None:
                return envs
            if name not in envs:
                raise SonarInvalidArgError
            return envs[name]

    @staticmethod
    def get_active():
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            return db["active"]["env"]

    @staticmethod
    def clear():
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            db["env"] = {}

    @staticmethod
    def activate(name):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            try:
                env = db["env"][name]
            except KeyError as exc:
                raise SonarInvalidArgError from exc
            active = db["active"]
            active["env"] = name
            db["active"] = active

        if env["board"]:
            Board.activate(env["board"])
        # else:
        #     Board.deactivate()
        if env["repo"]:
            Repo.activate(env["repo"])
        # else:
        #     Repo.deactivate()
        if env["cad"] or env["hls"] or env["sim"]:
            Tool.activate(env["cad"], env["hls"], env["sim"])
        # else:
        #     Tool.deactivate()

    @staticmethod
    def deactivate():
        Board.deactivate()
        Repo.deactivate()
        Tool.deactivate()

    @staticmethod
    def remove(name):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            env = db["env"]
            del env[name]
            db["env"] = env


class Board:
    @staticmethod
    def add(path):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            boards = db["board"]
            board_name = os.path.basename(path)
            boards[board_name] = path
            db["board"] = boards

    @staticmethod
    def remove(name):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            boards = db["board"]
            del boards[name]
            db["board"] = boards

    @staticmethod
    def clear():
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            db["board"] = {}
            active = db["active"]
            active["board"] = None
            db["active"] = active

    @staticmethod
    def get(name=None):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            boards = db["board"]
            if name is None:
                return boards
            if name not in boards:
                raise SonarInvalidArgError
            return boards[name]

    @staticmethod
    def activate(name):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            try:
                board = db["board"][name]
            except KeyError as exc:
                logger.error(
                    f"Could not find board: {name}. See boards with `sonar board info`"
                )
                raise SonarInvalidArgError from exc
            with open(Constants.SONAR_SHELL_BOARD_SOURCE, "w") as f:
                script = []
                board_settings = runpy.run_path(os.path.join(board, "__init__.py"))
                part = board_settings["PART"]
                if "BOARD" in board_settings:
                    board = board_settings["BOARD"]
                    script.append(f"export SONAR_VIVADO_BOARD={board}")
                script.append(f"export SONAR_BOARD_NAME={name}")
                script.append(f"export SONAR_PART={part}")
                part_family = Board._find_part_family(part)
                if part_family:
                    script.append(f"export SONAR_PART_FAMILY={part_family}")
                f.write("\n".join(script))
            active = db["active"]
            active["board"] = name
            db["active"] = active

    @staticmethod
    def deactivate():
        if os.path.exists(Constants.SONAR_SHELL_BOARD_SOURCE):
            os.remove(Constants.SONAR_SHELL_BOARD_SOURCE)
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            active = db["active"]
            active["board"] = None
            db["active"] = active

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
    def add(path=None):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            repos = db["repo"]
            if path is None:
                repo_path = os.getcwd()
            else:
                repo_path = path
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
            active = db["active"]
            active["repo"] = None
            db["active"] = active

    @staticmethod
    def get(name=None):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            repos = db["repo"]
            if name is None:
                return repos
            if name not in repos:
                raise SonarInvalidArgError
            return repos[name]

    @staticmethod
    def activate(name):
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            try:
                repo = db["repo"][name]
            except KeyError as exc:
                logger.error(
                    f"Could not find repo: {name}. See repos with `sonar repo show`"
                )
                raise SonarInvalidArgError from exc
            with open(Constants.SONAR_SHELL_REPO_SOURCE, "w") as f:
                script = []
                path = repo["path"]
                script.append(f"export SONAR_REPO={path}")
                f.write("\n".join(script))
            active = db["active"]
            active["repo"] = name
            db["active"] = active

    @staticmethod
    def deactivate():
        if os.path.exists(Constants.SONAR_SHELL_REPO_SOURCE):
            os.remove(Constants.SONAR_SHELL_REPO_SOURCE)
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            active = db["active"]
            active["repo"] = None
            db["active"] = active

    @staticmethod
    def get_active():
        with shelve.open(Constants.SONAR_DB_PATH) as db:
            return db["active"]["repo"]


class IP:
    @staticmethod
    def add_new(name, path):
        active_repo = Repo.get_active()
        repo = Repo.get(active_repo)
        repo_path = repo["path"]
        init_toml = os.path.join(repo_path, Constants.SONAR_CONFIG_FILE_PATH)
        init = toml.load(init_toml)
        init["project"]["ips"] = [name]
        if "ips" not in init:
            init["ips"] = {}
        init["ips"][name] = {"path": str(path).replace(str(repo_path), "")}
        with open(init_toml, "w") as f:
            toml.dump(init, f)

    # @staticmethod
    # def add_src(name, path, src_type):
    #     ip = IP._find_active_ip(path)
    #     active_repo = Repo.get_active()
    #     repo = Repo.get(active_repo)
    #     repo_path = repo["path"]
    #     init_toml = os.path.join(repo_path, Constants.SONAR_CONFIG_FILE_PATH)
    #     init = toml.load(init_toml)
    #     assert ip is not None

    #     if "src" not in init["ips"][ip]:
    #         init["ips"][ip]["src"] = {
    #             "c": [],
    #             "hdl": [],
    #             "custom": []
    #         }
    #     init["ips"][ip]["src"][src_type].append(name)
    #     with open(init_toml, "w") as f:
    #         toml.dump(init, f)

    #     # with shelve.open(Constants.SONAR_DB_PATH) as db:
    #     #     repos = db["repo"]
    #     #     repos[active_repo] = repo
    #     #     db["repo"] = repos

    # @staticmethod
    # def _find_active_ip(path):
    #     active_repo = Repo.get_active()
    #     repo = Repo.get(active_repo)
    #     repo_path = repo["path"]
    #     init_toml = os.path.join(repo_path, Constants.SONAR_CONFIG_FILE_PATH)
    #     init = toml.load(init_toml)
    #     if "ips" in init["project"]:
    #         for ip, ip_data in init["ips"].items():
    #             if path.endswith(ip_data["path"]):
    #                 return ip
    #         return None
    #     return None


# class SubscriptMixin:
#     def __getitem__(self, key):
#         return getattr(self, key)

#     def __setitem__(self, key, value):
#         setattr(self, key, value)


# class DBtools(SubscriptMixin):
#     def __init__(self):
#         self.cad_tool = {}
#         self.sim_tool = {}
#         self.hls_tool = {}

#     def __repr__(self):
#         return f"""\
#         {self.cad_tool}
#         {self.sim_tool}
#         {self.hls_tool}\
#         """

#     def __str__(self):
#         tool_str = ["cad:"]
#         tool_str.append(textwrap.indent(pprint.pformat(self.cad_tool), "    "))
#         tool_str.append("sim:")
#         tool_str.append(textwrap.indent(pprint.pformat(self.sim_tool), "    "))
#         tool_str.append("hls:")
#         tool_str.append(textwrap.indent(pprint.pformat(self.hls_tool), "    "))
#         return "\n".join(tool_str)


# class DBenvironment(SubscriptMixin):
#     def __init__(self, _cad_tool, _sim_tool, _hls_tool, _board, _project):
#         self.cad_tool = _cad_tool
#         self.sim_tool = _sim_tool
#         self.hls_tool = _hls_tool
#         self.board = _board
#         self.project = _project

#     def __repr__(self):
#         env_dict = {
#             "cad_tool": {self.cad_tool},
#             "sim_tool": {self.sim_tool},
#             "hls_tool": {self.hls_tool},
#             "board": {self.board},
#             "project": {self.project},
#         }
#         return str(env_dict)

#     def __str__(self):
#         return textwrap.dedent(
#             f"""\
#             Environment:
#                 cad_tool: {self.cad_tool}
#                 sim_tool: {self.sim_tool}
#                 hls_tool: {self.hls_tool}
#                 board: {self.board}
#                 project: {self.project}\
#             """
#         )


# class DBtool(SubscriptMixin):
#     def __init__(self, _name, _version, _script):
#         self.name = _name
#         self.version = _version
#         self.script = _script

#     def __repr__(self):
#         return f"<database.Tool()>"

#     def __str__(self):
#         return textwrap.dedent(
#             f"""\
#             name: {self.name}
#             version: {self.version}
#             script: {self.script}\
#             """
#         )


# class Repo(SubscriptMixin):
#     def __init__(self, _name, _path):
#         self.name = _name
#         self.path = _path

#         self.script = f"export SONAR_REPO_PATH={_path}"

#     def __repr__(self):
#         return f"<database.Repo()>"

#     def __str__(self):
#         return textwrap.dedent(
#             f"""\
#             name: {self.name}
#             path: {self.path}
#             script: {self.script}\
#             """
#         )


# class Board(SubscriptMixin):
#     def __init__(self, _name, _part):
#         self.name = _name
#         self.part = _part

#         self.script = textwrap.dedent(
#             f"""\
#             export SONAR_BOARD={_name}"
#             export SONAR_PART={_part}

#         """
#         )

#     def __repr__(self):
#         return f"<database.Board({self.name}, {self.part}, {self.script})>"

#     def __str__(self):
#         return textwrap.dedent(
#             f"""\
#             name: {self.name}
#             part: {self.part}
#             script: {self.script}\
#             """
#         )


def print_db():
    with shelve.open(Constants.SONAR_DB_PATH, "r") as db:
        dkeys = list(db.keys())
        dkeys.sort()
        for x in dkeys:
            print(x, pprint.pformat(db[x]))


def check_database():
    try:
        db = shelve.open(Constants.SONAR_DB_PATH, "r")
    except dbm.error:
        return False
    else:
        db.close()
        return True
