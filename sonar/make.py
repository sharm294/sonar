import os
import textwrap
import sonar.database as Database


class MakeFile:
    def __init__(self):
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
        self.phony = []

    def ip(self, ip_dir):
        self._add_ip_variables(ip_dir)
        self._add_obj_deps()
        self._add_src_objs()
        self._add_ip_phony()
        return str(self)

    def _add_ip_variables(self, ip_dir):
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
        self.variables.append(("test_bin_dir", "$(test_dir)/build/bin"))
        self.variables.append(("include_dir", "$(ip_dir)/include"))
        self.variables.append(("hls_dir", "$(ip_dir)/hls"))
        self.variables.append(("cad_dir", "$(ip_dir)/cad"))
        self.variables.append(None)

        self.cflags.local_include.append("$(include_dir)")

    def _add_obj_deps(self):
        self.variables.append(
            (
                "obj",
                "$(shell find $(build_dir) -name '*.o' -printf '%f\\n' | sort -k 1nr | cut -f2-)",
            )
        )
        self.variables.append(("dep", "$(obj:%.o=$(build_dir)/%.d)"))
        self.variables.append(None)

    def _add_src_objs(self):
        self.variables.append(("c_modules", ""))
        self.variables.append(("hdl_modules", ""))
        self.variables.append(("custom_modules", ""))
        self.variables.append(None)

    def _add_header(self, title):
        return textwrap.dedent(
            f"""
        ################################################################################
        # {title}
        ################################################################################

        """
        )

    def _add_light_header(self, title):
        return textwrap.dedent(
            f"""
        #-------------------------------------------------------------------------------
        # {title}
        #-------------------------------------------------------------------------------

        """
        )

    def _add_ip_phony(self):
        self.phony.extend(["test", "hw", "sim", "clean"])

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
            if not variable:
                makefile += "\n"
            else:
                makefile += variable[0] + " = " + variable[1] + "\n"

        makefile += f"CC = {self.compiler}\n"
        makefile += f"CFLAGS = {str(self.cflags)}\n"

        makefile += self._add_header("Body")

        makefile += ".PHONY: "
        for target in self.phony:
            makefile += target + " "
        makefile += "\n\n"

        # for now, giving up on generic and just hardcoding what's needed
        makefile += self._add_light_header("Sonar Testbench Generation")

        makefile += textwrap.dedent(
            """\
            config_modules=$(patsubst %, config-%, $(c_modules))
            config_modules+=$(patsubst %, config-%, $(hdl_modules))
            config_modules+=$(patsubst %, config-%, $(custom_modules))
            config: $(config_modules)

            # Overwrites .dat file in sim folders if the file already exists there
            define make-config
            config-$1: guard-SONAR_PATH
            \t@python $(test_dir)/$1.py
            \t@$(eval $1_sim_path = $(cad_dir)/projects/$(SONAR_CAD_VERSION)/$(SONAR_PART)/$1/$1.sim/sim_1/behav)
            \t@if [[ -f $($1_sim_path)/$1_sv.dat ]]; then cp $(test_build_dir)/$1/$1_sv.dat $($1_sim_path); fi
            endef
            $(foreach module, $(c_modules),$(eval $(call make-config,$(module),all)))
            $(foreach module, $(hdl_modules),$(eval $(call make-config,$(module),sv)))
            $(foreach module, $(custom_modules),$(eval $(call make-config,$(module),sv)))
            """
        )

        makefile += self._add_light_header("Vivado HLS HW Generation")
        makefile += textwrap.dedent(
            """\
            hw_modules=$(patsubst %, hw-%, $(c_modules))
            hw: $(hw_modules)

            define make-hw
            hw-$1:
            \tenv | grep SONAR
            \t@$(hls_dir)/generate_hls.sh $1 # create Vivado HLS project and export the design
            \t@$(cad_dir)/generate_cad.sh $1 c # Symlink all generated files for Vivado
            endef
            $(foreach module, $(c_modules),$(eval $(call make-hw,$(module))))
            """
        )

        makefile += self._add_light_header("Vivado RTL Simulation")
        makefile += textwrap.dedent(
            """\
            sim_modules=$(patsubst %, sim-%, $(c_modules))
            sim_modules+=$(patsubst %, sim-%, $(hdl_modules))
            sim_modules+=$(patsubst %, sim-%, $(custom_modules))
            sim: $(sim_modules)

            define make-sim
            sim-$1: guard-VIV_MODE guard-VIV_SIM guard-VIV_CREATE guard-VIV_SYNTH guard-VIV_IMPL guard-VIV_BIT guard-VIV_EXPORT
            \t@if [[ $(VIV_CREATE) == 1 ]]; then $(cad_dir)/generate_cad.sh $1 $2; fi
            \t@vivado -mode $(VIV_MODE) -source $(cad_dir)/generate_cad.tcl -notrace \\
            \t\t-tclargs --project $1 --sim $(VIV_SIM) --create $(VIV_CREATE) \\
            \t\t--synth $(VIV_SYNTH) --impl $(VIV_IMPL) --bit $(VIV_BIT) --export $(VIV_EXPORT)
            endef
            $(foreach module, $(c_modules),$(eval $(call make-sim,$(module),c)))
            $(foreach module, $(hdl_modules),$(eval $(call make-sim,$(module),hdl)))

            define make-sim-custom
            sim-$1: guard-VIV_MODE guard-VIV_SIM guard-VIV_CREATE guard-VIV_SYNTH guard-VIV_IMPL guard-VIV_BIT guard-VIV_EXPORT
            \t@if [[ $(VIV_CREATE) == 1 ]]; then $(cad_dir)/$1.sh; fi
            \t@vivado -mode $(VIV_MODE) -source $(cad_dir)/generate_cad.tcl -notrace \\
            \t\t-tclargs --project $1 --sim $(VIV_SIM) --create $(VIV_CREATE) \\
            \t\t--synth $(VIV_SYNTH) --impl $(VIV_IMPL) --bit $(VIV_BIT) --export $(VIV_EXPORT)
            endef
            $(foreach module, $(custom_modules),$(eval $(call make-sim-custom,$(module))))"""
        )

        makefile += self._add_light_header("C++ Simulation")
        makefile += textwrap.dedent(
            """\
            define run-executable
            runtb-$1: cpptb-$1
            \t$(test_bin_dir)/$1_tb
            endef
            $(foreach module, $(c_modules),$(eval $(call run-executable,$(module))))

            define make-executable
            cpptb-$1: $(test_build_dir)/$1_tb.o $(build_dir)/$1.o
            \t$(CC) $(CFLAGS) -o $(test_bin_dir)/$1_tb $(test_build_dir)/$1_tb.o $(build_dir)/$1.o
            endef
            $(foreach module, $(c_modules),$(eval $(call make-executable,$(module))))

            define make-testbench
            $(test_build_dir)/$1_tb.o: $(test_build_dir)/$1/$1_tb.cpp
            \t$(CC) $(CFLAGS) -o $(test_build_dir)/$1_tb.o -c $(test_build_dir)/$1/$1_tb.cpp
            endef
            $(foreach module, $(c_modules),$(eval $(call make-testbench,$(module))))

            define make-object
            $(build_dir)/$1.o: $(src_dir)/$1.cpp
            \t$(CC) $(CFLAGS) -o $(build_dir)/$1.o -c $(src_dir)/$1.cpp
            endef
            $(foreach module, $(c_modules),$(eval $(call make-object,$(module))))"""
        )

        return makefile


class CFlags:
    def __init__(self):
        self.debug = True
        self.local_include = []
        if os.getenv("SONAR_HLS_INCLUDE") is not None:
            self.system_include = ["$(SONAR_HLS_INCLUDE)"]
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
            cflags.append("-g -O0")

        for include in self.local_include:
            cflags.append(f"-I{include}")

        for include in self.system_include:
            cflags.append(f"-isystem{include}")

        cflags.append(" ".join(self.errors))

        if self.dependency:
            cflags.append("-MMD -MP")

        return " ".join(cflags)
