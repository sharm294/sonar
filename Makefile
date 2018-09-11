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
path of of the share repository root. Did you source init.sh?)
endif

ifndef SONAR_VIVADO_HLS
$(error SONAR_VIVADO_HLS not set in env -- must be set to the absolute \
path of of the Vivado HLS include/ directory. Did you source init.sh?)
endif

sample_dir = $(SONAR_PATH)/sample
sample_obj_dir = $(sample_dir)/build
sample_bin_dir = $(sample_obj_dir)/bin

obj = $(shell find $(sample_obj_dir)/ -name '*.o' -printf '%f\n' | \
sort -k 1nr | cut -f2-)
dep = $(obj:%.o=$(obj_dir)/%.d)

CC = g++
CFLAGS = -g -Wall -I$(SONAR_PATH)/include -I$(SONAR_VIVADO_HLS) \
	-Wno-unknown-pragmas -Wno-comment -MMD -MP

###############################################################################
# Body
###############################################################################

.PHONY: sample hw clean purge

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

sample: $(sample_bin_dir)/sample_tb
	@python $(SONAR_PATH)/sonar.py env SONAR_PATH /sample/sample.yaml
	@$(sample_bin_dir)/sample_tb

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

purge: clean
	@rm -rf ~/.sonar
	@sed -i '/added by sonar/d' ~/.bashrc