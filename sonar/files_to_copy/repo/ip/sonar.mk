################################################################################
# Include
################################################################################

include $(SONAR_PATH)/make/include.mk

################################################################################
# Prologue
################################################################################

MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL :=
.DELETE_ON_ERROR:
.SUFFIXES:

################################################################################
# Variables
################################################################################

global_include_dir = $(SHOAL_PATH)/include

local_dir = $(SHOAL_PATH)/GAScore
obj_dir = $(local_dir)/build
bin_dir = $(local_dir)/build/bin
src_dir = $(local_dir)/src
test_dir = $(local_dir)/testbench
test_build_dir = $(test_dir)/build
local_include_dir = $(local_dir)/include
hls_dir = $(local_dir)/vivado_hls
vivado_dir = $(local_dir)/vivado
repo_path = $(local_dir)/repo

helper_dir = $(SHOAL_PATH)/helper
helper_obj_dir = $(helper_dir)/build
helper_bin_dir = $(helper_dir)/build/bin
helper_include_dir = $(helper_dir)/include

c_modules := am_rx am_tx xpams_rx hold_buffer xpams_tx handler hold_buffer_dest
hdl_modules := memory add_id
custom_modules := handler_wrapper GAScore
test_projects := MB_GAScore_0 MB_GAScore_1

obj = $(shell find $(obj_dir) -name '*.o' -printf '%f\n' | \
sort -k 1nr | cut -f2-)
helper_obj = $(shell find $(helper_obj_dir) -name '*.o' -printf '%f\n' | \
sort -k 1nr | cut -f2-)
dep = $(obj:%.o=$(obj_dir)/%.d)
dep += $(helper_obj:%.o=$(helper_obj_dir)/%.d)

CC = g++
CFLAGS = -g -Wall -I$(local_include_dir) -I$(helper_include_dir) -I$(global_include_dir)\
	-isystem $(SHOAL_HLS_PATH)/$(SHOAL_HLS_VERSION)/include \
	-Wno-unknown-pragmas -Wno-comment -Wno-shift-count-overflow -MMD -MP

################################################################################
# Body
################################################################################

.PHONY: test hw sim clean

#-------------------------------------------------------------------------------
# C++ Testbench Execution
#-------------------------------------------------------------------------------

test_modules=$(patsubst %, test-%, $(c_modules))
test: $(test_modules)

define make-test
test-$1: $(bin_dir)/$1_tb
	@$(bin_dir)/$1_tb --readInterfaces
endef
$(foreach module, $(c_modules),$(eval $(call make-test,$(module))))

#-------------------------------------------------------------------------------
# Sonar Testbench Generation
#-------------------------------------------------------------------------------

config_modules=$(patsubst %, config-%, $(c_modules))
config_modules+=$(patsubst %, config-%, $(hdl_modules))
config_modules+=$(patsubst %, config-%, $(custom_modules))
config: $(config_modules)

# Overwrites .dat file in sim folders if the file already exists there
define make-config
config-$1: guard-SONAR_PATH
	@python $(test_dir)/$1.py
	@$(eval $1_sim_path = $(vivado_dir)/projects/$(SHOAL_VIVADO_VERSION)/$(SHOAL_PART)/$1/$1.sim/sim_1/behav)
	@if [[ -f $($1_sim_path)/$1_sv.dat ]]; then cp $(test_build_dir)/$1/$1_sv.dat $($1_sim_path); fi
	@$(eval $1_sim_path = $(vivado_dir)/projects/$(SHOAL_VIVADO_VERSION)/$(SHOAL_PART)/$1/$1.sim/sim_1/synth/func)
	@if [[ -f $($1_sim_path)/$1_sv.dat ]]; then cp $(test_build_dir)/$1/$1_sv.dat $($1_sim_path); fi
endef
$(foreach module, $(c_modules),$(eval $(call make-config,$(module),all)))
$(foreach module, $(hdl_modules),$(eval $(call make-config,$(module),sv)))
$(foreach module, $(custom_modules),$(eval $(call make-config,$(module),sv)))

#-------------------------------------------------------------------------------
# Vivado HLS HW Generation
#-------------------------------------------------------------------------------

hw_modules=$(patsubst %, hw-%, $(c_modules))
hw: $(hw_modules)

define make-hw
hw-$1:
	@$(hls_dir)/generate.sh $1 # create Vivado HLS project and export the design
	@$(vivado_dir)/generate.sh $1 c # Symlink all generated files for Vivado
endef
$(foreach module, $(c_modules),$(eval $(call make-hw,$(module))))

package:
	@mkdir -p $(SHOAL_PATH)/GAScore/vivado/projects/$(SHOAL_VIVADO_VERSION)/$(SHOAL_PART)/temp
	@mkdir -p $(SHOAL_PATH)/repo/$(SHOAL_VIVADO_VERSION)/$(SHOAL_PART_FAMILY)/GAScore
	@rm -rf $(SHOAL_PATH)/repo/$(SHOAL_VIVADO_VERSION)/$(SHOAL_PART_FAMILY)/GAScore/*
	@vivado -mode batch -source $(local_dir)/GAScore_package.tcl -notrace
	@unzip -o $(SHOAL_PATH)/repo/$(SHOAL_VIVADO_VERSION)/$(SHOAL_PART_FAMILY)/GAScore/GAScore.zip -d $(SHOAL_PATH)/repo/$(SHOAL_VIVADO_VERSION)/$(SHOAL_PART_FAMILY)/GAScore/
	@rm $(SHOAL_PATH)/repo/$(SHOAL_VIVADO_VERSION)/$(SHOAL_PART_FAMILY)/GAScore/GAScore.zip
	@rm -rf $(SHOAL_PATH)/GAScore/vivado/projects/$(SHOAL_VIVADO_VERSION)/$(SHOAL_PART)/temp

#-------------------------------------------------------------------------------
# Vivado RTL Simulation
#-------------------------------------------------------------------------------

sim_modules=$(patsubst %, sim-%, $(c_modules))
sim_modules+=$(patsubst %, sim-%, $(hdl_modules))
sim_modules+=$(patsubst %, sim-%, $(custom_modules))
sim: $(sim_modules)

define make-sim
sim-$1: guard-VIV_MODE guard-VIV_SIM guard-VIV_CREATE guard-VIV_SYNTH guard-VIV_IMPL guard-VIV_BIT guard-VIV_EXPORT
	@if [[ $(VIV_CREATE) == 1 ]]; then $(vivado_dir)/generate.sh $1 $2; fi
	@vivado -mode $(VIV_MODE) -source $(vivado_dir)/generate.tcl -notrace \
		-tclargs --project $1 --sim $(VIV_SIM) --create $(VIV_CREATE) \
		--synth $(VIV_SYNTH) --impl $(VIV_IMPL) --bit $(VIV_BIT) --export $(VIV_EXPORT)
endef
$(foreach module, $(c_modules),$(eval $(call make-sim,$(module),c)))
$(foreach module, $(hdl_modules),$(eval $(call make-sim,$(module),hdl)))

define make-sim-custom
sim-$1: guard-VIV_MODE guard-VIV_SIM guard-VIV_CREATE guard-VIV_SYNTH guard-VIV_IMPL guard-VIV_BIT guard-VIV_EXPORT
	@if [[ $(VIV_CREATE) == 1 ]]; then $(vivado_dir)/$1.sh; fi
	@vivado -mode $(VIV_MODE) -source $(vivado_dir)/generate.tcl -notrace \
		-tclargs --project $1 --sim $(VIV_SIM) --create $(VIV_CREATE) \
		--synth $(VIV_SYNTH) --impl $(VIV_IMPL) --bit $(VIV_BIT) --export $(VIV_EXPORT)
endef
$(foreach module, $(custom_modules),$(eval $(call make-sim-custom,$(module))))

define make-sim-test
sim-$1: guard-VIV_MODE guard-VIV_SIM guard-VIV_CREATE guard-VIV_SYNTH guard-VIV_IMPL guard-VIV_BIT guard-VIV_EXPORT
	@if [[ $(VIV_CREATE) == 1 ]]; then $(vivado_dir)/$1.sh; fi
	@vivado -mode $(VIV_MODE) -source $(vivado_dir)/generate.tcl -notrace \
		-tclargs --project $1 --sim $(VIV_SIM) --create $(VIV_CREATE) \
		--synth $(VIV_SYNTH) --impl $(VIV_IMPL) --bit $(VIV_BIT) --export $(VIV_EXPORT)
	@xsct $(vivado_dir)/$1_sdk.tcl
endef
$(foreach module, $(test_projects),$(eval $(call make-sim-test,$(module))))

#-------------------------------------------------------------------------------
# C++ Executable Generation
#-------------------------------------------------------------------------------

define make-executable
$(bin_dir)/$1_tb: $(obj_dir)/utilities.o $(obj_dir)/$1_tb.o $(obj_dir)/$1.o
	$(CC) $(CFLAGS) -o $(bin_dir)/$1_tb $(obj_dir)/utilities.o \
		$(obj_dir)/$1_tb.o $(obj_dir)/$1.o
endef
$(foreach module, $(c_modules),$(eval $(call make-executable,$(module))))

#-------------------------------------------------------------------------------
# Object Files Generation
#-------------------------------------------------------------------------------

define make-testbench
$(obj_dir)/$1_tb.o: $(test_build_dir)/$1/$1_tb.cpp
	$(CC) $(CFLAGS) -o $(obj_dir)/$1_tb.o -c $(test_build_dir)/$1/$1_tb.cpp
endef
$(foreach module, $(c_modules),$(eval $(call make-testbench,$(module))))

$(obj_dir)/utilities.o: $(src_dir)/utilities.cpp
	$(CC) $(CFLAGS) -o $(obj_dir)/utilities.o -c $(src_dir)/utilities.cpp

define make-object
$(obj_dir)/$1.o: $(src_dir)/$1.cpp
	$(CC) $(CFLAGS) -o $(obj_dir)/$1.o -c $(src_dir)/$1.cpp
endef
$(foreach module, $(c_modules),$(eval $(call make-object,$(module))))

-include $(dep)

#-------------------------------------------------------------------------------
# Cleanup
#-------------------------------------------------------------------------------

shoal_make = $(MAKE) --no-print-directory -f $(SHOAL_PATH)/Makefile $1

clean:
	@$(call shoal_make, clean)
clean-1:
	@$(call shoal_make, clean-1)

	# @rm -rf $(obj_dir)/*.o $(obj_dir)/*.d $(bin_dir)/* \
	# $(helper_obj_dir)/*.o $(helper_obj_dir)/*.d $(helper_bin_dir)/* \
	# $(test_build_dir)/*
