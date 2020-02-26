import textwrap
import pprint
import shelve
import logging
import os

from sonar.include import Constants
from sonar.exceptions import SonarInvalidArgError, SonarInvalidOpError

logger = logging.getLogger(__name__)


class Database:
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
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                env = db["env"]
                env[args.name] = DBenvironment(
                    args.cad_tool, args.sim_tool, args.hls_tool
                )
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

    class Board:
        @staticmethod
        def add(args):
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                boards = db["board"]
                board_name = os.path.basename(args.path)
                boards[board_name] = args.path
                db["board"] = boards

        @staticmethod
        def clear():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                db["board"] = {}

        @staticmethod
        def get():
            with shelve.open(Constants.SONAR_DB_PATH) as db:
                boards = db["board"]
            return boards

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
            with open(Constants.SONAR_BASH_ENV_SOURCE, "w") as f:
                script = []
                for key in ["cad_tool", "sim_tool", "hls_tool"]:
                    tool_id = env[key]
                    tool_script = db["tool"][tool_id[0]]["script"][tool_id[1]]
                    if tool_script not in script:
                        script.append(tool_script)
                f.write("\n".join(script))


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
    def __init__(self, _cad_tool, _sim_tool, _hls_tool):
        self.cad_tool = _cad_tool
        self.sim_tool = _sim_tool
        self.hls_tool = _hls_tool

    def __repr__(self):
        return "<database.Environment()>"

    def __str__(self):
        return textwrap.dedent(
            f"""\
            Environment:
                cad_tool: {self.cad_tool}
                sim_tool: {self.sim_tool}
                hls_tool: {self.hls_tool}\
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


def print_db(db):
    dkeys = list(db.keys())
    dkeys.sort()
    for x in dkeys:
        print(x, db[x])
