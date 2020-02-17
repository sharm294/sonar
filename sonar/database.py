import textwrap


class Environment:
    def __init__(self):
        self.cad_tool = {}
        self.sim_tool = {}
        self.hls_tool = {}
        self.repo = {}
        self.board = {}

    def __repr__(self):
        return f"""\
        {self.cad_tool}
        {self.sim_tool}
        {self.hls_tool}
        {self.repo}
        {self.board}\
        """

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


class Tool:
    def __init__(self, _name, _version, _script):
        self.name = _name
        self.version = _version
        self.script = _script

    def __repr__(self):
        return f"<database.Tool({self.name}, {self.version}, {self.script})>"

    def __str__(self):
        return textwrap.dedent(
            f"""\
            name: {self.name}
            version: {self.version}
            script: {self.script}\
            """
        )


class HLSTool(Tool):
    def __init__(self, _name, _version, _script, _include):
        super().__init__(_name, _version, _script)
        self.include = _include

    def __str__(self):
        return textwrap.dedent(
            f"""\
            name: {self.name}
            version: {self.version}
            script: {self.script}
            include: {self.include}\
            """
        )

    def __repr__(self):
        return f"<database.HLSTool({self.name}, {self.version}, {self.script}, {self.include})>"


def print_db(db):
    dkeys = list(db.keys())
    dkeys.sort()
    for x in dkeys:
        print(x, db[x])
