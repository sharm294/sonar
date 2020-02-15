class Environment:
    def __init__(self):
        self.cad_tool = {}
        self.sim_tool = {}
        self.hls_tool = {}
        self.repo = {}
        self.hls_include = {}
        self.board = {}
        self.part = {}
        self.cad_version = {}
        self.sim_version = {}
        self.hls_version = {}

    def __repr__(self):
        return f"""
        {self.cad_tool}
        {self.sim_tool}
        {self.hls_tool}
        {self.repo}
        {self.hls_include}
        {self.board}
        {self.part}
        {self.cad_version}
        {self.sim_version}
        {self.hls_version}
        """


def print_db(db):
    dkeys = list(db.keys())
    dkeys.sort()
    for x in dkeys:
        print(x, db[x])
