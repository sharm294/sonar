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

SHOAL_SHARE_PATH = "/home/sharm294/Documents/masters/git_repos/shoal/shoal-share"
SHOAL_VIVADO_HLS_INC = "/media/sharm294/HDD_1TB/Xilinx/Vivado_HLS/2017.2/include"

sample_dir = $(SHOAL_SHARE_PATH)/sample
sample_obj_dir = $(sample_dir)/build
sample_bin_dir = $(sample_obj_dir)/bin
JSON_testbench_dir = $(SHOAL_SHARE_PATH)/JSON-testbench

obj = $(shell find $(sample_obj_dir) -name '*.o' -printf '%f\n' | \
sort -k 1nr | cut -f2-)
dep = $(obj:%.o=$(obj_dir)/%.d)

CC = g++
CFLAGS = -g -Wall -I./include -I$(SHOAL_VIVADO_HLS_INC) \
	-Wno-unknown-pragmas -Wno-comment -MMD -MP

###############################################################################
# Body
###############################################################################

.PHONY: init sample hw clean

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

sample: $(sample_bin_dir)/sample_tb
	python $(JSON_testbench_dir)/generate.py absolute None $(JSON_testbench_dir)/sample/sample.json
	$(sample_bin_dir)/sample_tb

init:
	mkdir -p $(sample_obj_dir)
	mkdir -p $(sample_bin_dir)
	./init.sh $(SHOAL_SHARE_PATH) $(SHOAL_VIVADO_HLS_INC)

hw:
	$(sample_dir)/sample.sh

#------------------------------------------------------------------------------
# Executables
#------------------------------------------------------------------------------

$(sample_bin_dir)/sample_tb: $(sample_obj_dir)/sample_tb.o $(sample_obj_dir)/sample.o
	$(CC) $(CFLAGS) -o $(sample_bin_dir)/sample_tb $(sample_obj_dir)/sample_tb.o \
	$(sample_obj_dir)/sample.o

#------------------------------------------------------------------------------
# Object Files
#------------------------------------------------------------------------------

$(sample_obj_dir)/sample_tb.o: $(sample_dir)/sample_tb.cpp
	$(CC) $(CFLAGS) -o $(sample_obj_dir)/sample_tb.o -c $(sample_dir)/sample_tb.cpp

$(sample_obj_dir)/sample.o: $(sample_dir)/sample.cpp
	$(CC) $(CFLAGS) -o $(sample_obj_dir)/sample.o -c $(sample_dir)/sample.cpp

-include $(dep)

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------

clean: 
	@$(RM) $(sample_obj_dir)/*.o $(sample_obj_dir)/*.d $(sample_bin_dir)/*
