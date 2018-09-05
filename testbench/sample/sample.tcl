### default setting
set Project     sample
set Solution    Virtex_Ultrascale
set Device      "xcvu095-ffvc1517-2-e"
set Flow        ""
set Clock       4.0
set DefaultFlag 1

set local_include -I${::env(SHOAL_SHARE_PATH)}/sample
set share_include -I${::env(SHOAL_SHARE_PATH)}/include
append include local_include " " share_include

#### main part

# Project settings
open_project $Project -reset

# Add the file for synthesis
add_files sample.cpp -cflags $include

# Add testbench files for co-simulation
add_files -tb sample_tb.cpp -cflags $include

# Set top module of the design
set_top sample

# Solution settings
open_solution -reset $Solution

# Add library
set_part $Device

# Set the target clock period
create_clock -period $Clock

# Set up the config
config_interface -register_io off
config_rtl -reset state -reset_level low

#################
# C SIMULATION
#################
csim_design

#############
# SYNTHESIS #
#############
csynth_design

#################
# CO-SIMULATION #
#################
#cosim_design -rtl verilog -trace_level all

##################
# IMPLEMENTATION #
##################
export_design -format ipxact

exit
