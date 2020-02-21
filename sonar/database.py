import textwrap
import pprint


# https://stackoverflow.com/a/32107024
class DotDict(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for arg in args:
        #     if isinstance(arg, dict):
        #         for k, v in arg.items():
        #             self[k] = v

        # if kwargs:
        #     for k, v in kwargs.items():
        #         self[k] = v
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
    # def __getattr__(self, attr):
    #     return getattr(self, attr)

    # def __setattr__(self, key, value):
    #     setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Tools(SubscriptMixin):
    def __init__(self):
        # super().__init__({
        #     "cad_tool": {},
        #     "sim_tool": {},
        #     "hls_tool": {},
        #     "repo": {},
        #     "board": {},
        # })
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


class Environment(SubscriptMixin):
    def __init__(self, _cad_tool, _sim_tool, _hls_tool, _repo, _board):
        self.cad_tool = _cad_tool
        self.sim_tool = _sim_tool
        self.hls_tool = _hls_tool
        self.repo = _repo
        self.board = _board

    def __repr__(self):
        return "<database.Environment()>"

    def __str__(self):
        return textwrap.dedent(
            f"""\
            Environment:
                cad_tool: {self.cad_tool}
                sim_tool: {self.sim_tool}
                hls_tool: {self.hls_tool}
                repo: {self.repo}
                board: {self.board}\
            """
        )


class Tool(SubscriptMixin):
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
