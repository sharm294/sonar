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

ifdef SONAR_PATH
sample_dir = $(SONAR_PATH)/sample
sample_obj_dir = $(sample_dir)/build
sample_bin_dir = $(sample_obj_dir)/bin

obj = $(shell find $(sample_obj_dir)/ -name '*.o' -printf '%f\n' | \
sort -k 1nr | cut -f2-)
dep = $(obj:%.o=$(obj_dir)/%.d)
endif

ifdef SONAR_VIVADO_HLS
CC = g++
CFLAGS = -g -Wall -I$(SONAR_VIVADO_HLS) \
	-Wno-unknown-pragmas -Wno-comment -MMD -MP
EXECUTABLES = vivado vivado_hls bash gcc
else
EXECUTABLES = bash gcc
endif

K := $(foreach exec,$(EXECUTABLES),\
        $(if $(shell which $(exec)),some string,$(error "No $(exec) in PATH")))

###############################################################################
# Body
###############################################################################

.PHONY: sample sample_hw sample_sim clean purge sample_gen sample_csim

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set. Have you sourced init.sh?"; \
		exit 1; \
	fi

ifdef SONAR_VIVADO_HLS
sample: sample_hw sample_gen sample_csim sample_sim
else
sample: sample_gen sample_sim
endif

# creates a Vivado HLS project and export Sample to RTL
sample_hw: guard-SONAR_PATH guard-SONAR_VIVADO_HLS
	@$(sample_dir)/sample_hls.sh

# performs C-simulation on sample
sample_csim: guard-SONAR_PATH $(sample_bin_dir)/sample_tb
	@$(sample_bin_dir)/sample_tb

# generate the testbenches and data files
ifdef SONAR_VIVADO_HLS
sample_gen: guard-SONAR_PATH
	@python $(SONAR_PATH)/sample/sample.py $(SONAR_PATH)/sample/build/sample/ all
else
sample_gen: guard-SONAR_PATH
	@python $(SONAR_PATH)/sample/sample.py $(SONAR_PATH)/sample/build/sample/ sv
endif

# creates a Vivado project, adds all the files and opens Vivado for simulation
sample_sim: guard-SONAR_PATH
	@vivado -mode batch -notrace -source $(sample_dir)/sample_vivado.tcl

#------------------------------------------------------------------------------
# Executables
#------------------------------------------------------------------------------

$(sample_bin_dir)/sample_tb: guard-SONAR_PATH $(sample_obj_dir)/sample_tb.o $(sample_obj_dir)/sample.o
	$(CC) $(CFLAGS) -o $(sample_bin_dir)/sample_tb $(sample_obj_dir)/sample_tb.o \
		$(sample_obj_dir)/sample.o

#------------------------------------------------------------------------------
# Object Files
#------------------------------------------------------------------------------

$(sample_obj_dir)/sample_tb.o: guard-SONAR_PATH $(sample_dir)/build/sample/sample_tb.cpp
	$(CC) $(CFLAGS) -I$(SONAR_PATH)/sample -o $(sample_obj_dir)/sample_tb.o \
		-c $(sample_dir)/build/sample/sample_tb.cpp

$(sample_obj_dir)/sample.o: guard-SONAR_PATH $(sample_dir)/sample.cpp
	$(CC) $(CFLAGS) -I$(SONAR_PATH)/sample -o $(sample_obj_dir)/sample.o \
		-c $(sample_dir)/sample.cpp

-include $(dep)

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------

clean: guard-SONAR_PATH
	@$(RM) $(sample_obj_dir)/*.o $(sample_obj_dir)/*.d $(sample_bin_dir)/*
	@$(RM) vivado*.jou vivado*.log	