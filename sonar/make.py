import os
import textwrap
import sonar.database as Database


class MakeFile:
    def __init__(self,):
        self.include = ["$(SONAR_PATH)/make/include.mk"]
        self.prologue = [
            "MAKEFLAGS += --warn-undefined-variables",
            "SHELL := bash",
            ".SHELLFLAGS := -eu -o pipefail -c",
            ".DEFAULT_GOAL :=",
            ".DELETE_ON_ERROR:",
            ".SUFFIXES:",
        ]
        self.variables = []
        self.compiler = "g++"
        self.cflags = CFlags()

    def add_ip_variables(self, ip_dir):
        # ip_dir_env = "$(SONAR_REPO)" + ip_dir.replace(os.environ["SONAR_REPO"], "")
        active_repo = Database.Repo.get_active()
        path = Database.Repo.get(active_repo)["path"]
        ip_dir_env = "$(SONAR_REPO)" + ip_dir.replace(path, "")
        self.variables.append(("ip_dir", ip_dir_env))
        self.variables.append(("build_dir", "$(ip_dir)/build"))
        self.variables.append(("bin_dir", "$(ip_dir)/build/bin"))
        self.variables.append(("src_dir", "$(ip_dir)/src"))
        self.variables.append(("test_dir", "$(ip_dir)/testbench"))
        self.variables.append(("test_build_dir", "$(test_dir)/build"))
        self.variables.append(("include_dir", "$(ip_dir)/include"))
        self.variables.append(("hls_dir", "$(ip_dir)/hls"))
        self.variables.append(("cad_dir", "$(ip_dir)/cad"))
        self.variables.append(("include_dir", "$(ip_dir)/include"))

        self.cflags.local_include.append("$(include_dir)")

    def _add_header(self, title):
        return textwrap.dedent(
            f"""
        ################################################################################
        # {title}
        ################################################################################

        """
        )

    def __str__(self):
        makefile = ""

        makefile += self._add_header("Include")
        for include in self.include:
            makefile += "include " + include + "\n"

        makefile += self._add_header("Prologue")
        for prologue in self.prologue:
            makefile += prologue + "\n"

        makefile += self._add_header("Variables")
        for variable in self.variables:
            makefile += variable[0] + " = " + variable[1] + "\n"

        makefile += f"\nCC = {self.compiler}\n"
        makefile += f"CFLAGS = {str(self.cflags)}\n"

        return makefile


class CFlags:
    def __init__(self):
        self.debug = True
        self.local_include = []
        if "SONAR_HLS_INCLUDE" in os.environ:
            self.system_include = [os.environ["SONAR_HLS_INCLUDE"]]
        else:
            self.system_include = []
        self.errors = [
            "-Wall",
            "-Wno-unknown-pragmas",
            "-Wno-comment",
            "-Wno-shift-count-overflow",
        ]
        self.dependency = True

    def __str__(self):
        cflags = []

        if self.debug:
            cflags.append("-g")

        for include in self.local_include:
            cflags.append(f"-I{include}")

        for include in self.system_include:
            cflags.append(f"-isystem{include}")

        cflags.append(" ".join(self.errors))

        if self.dependency:
            cflags.append("-MMD -MP")

        return " ".join(cflags)
