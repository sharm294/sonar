###############################################################################
# Include
###############################################################################

###############################################################################
# Prologue
###############################################################################

MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := sample
.DELETE_ON_ERROR:
.SUFFIXES:

###############################################################################
# Variables
###############################################################################

ifndef SONAR_PATH
$(error SONAR_PATH not set in env -- must be set to the absolute \
path of repository root. Did you source init.sh?)
endif

sample_dir = $(SONAR_PATH)/sample
sample_obj_dir = $(sample_dir)/build
sample_bin_dir = $(sample_obj_dir)/bin

obj = $(shell find $(sample_obj_dir)/ -name '*.o' -printf '%f\n' | \
sort -k 1nr | cut -f2-)
dep = $(obj:%.o=$(obj_dir)/%.d)

CC = g++
ifdef SONAR_VIVADO_HLS
CFLAGS = -g -Wall -I$(SONAR_VIVADO_HLS) \
	-Wno-unknown-pragmas -Wno-comment -MMD -MP
else
CFLAGS = -g -Wall \
	-Wno-unknown-pragmas -Wno-comment -MMD -MP
endif

###############################################################################
# Body
###############################################################################

.PHONY: sample sample_hw sample_sim clean purge sample_gen sample_csim

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

init:
	@source init.sh

sample: sample_hw sample_gen sample_csim sample_sim

# creates a Vivado HLS project and export Sample to RTL
sample_hw:
	@$(sample_dir)/sample_hls.sh

# generate the testbenches and data files
sample_gen:
	@python $(SONAR_PATH)/src/sonar.py env SONAR_PATH /sample/sample.json all 

# performs C-simulation on sample
sample_csim: $(sample_bin_dir)/sample_tb
	@$(sample_bin_dir)/sample_tb

# creates a Vivado project, adds all the files and opens Vivado for simulation
sample_sim:
	@vivado -mode batch -notrace -source $(sample_dir)/sample_vivado.tcl

#------------------------------------------------------------------------------
# Executables
#------------------------------------------------------------------------------

$(sample_bin_dir)/sample_tb: $(sample_obj_dir)/sample_tb.o $(sample_obj_dir)/sample.o
	$(CC) $(CFLAGS) -o $(sample_bin_dir)/sample_tb $(sample_obj_dir)/sample_tb.o \
		$(sample_obj_dir)/sample.o

#------------------------------------------------------------------------------
# Object Files
#------------------------------------------------------------------------------

$(sample_obj_dir)/sample_tb.o: $(sample_dir)/build/sample/sample_tb.cpp
	$(CC) $(CFLAGS) -I$(SONAR_PATH)/sample -o $(sample_obj_dir)/sample_tb.o \
		-c $(sample_dir)/build/sample/sample_tb.cpp

$(sample_obj_dir)/sample.o: $(sample_dir)/sample.cpp
	$(CC) $(CFLAGS) -I$(SONAR_PATH)/sample -o $(sample_obj_dir)/sample.o \
		-c $(sample_dir)/sample.cpp

-include $(dep)

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------

clean: 
	@$(RM) $(sample_obj_dir)/*.o $(sample_obj_dir)/*.d $(sample_bin_dir)/*
	@$(RM) vivado*.jou vivado*.log

purge: clean
	@rm -rf ~/.sonar
	@rm -rf $(SONAR_PATH)/sample/build
	@sed -i '/added by sonar/d' ~/.bashrc