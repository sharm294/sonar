################################################################################
# Parse Arguments
################################################################################

if { $::argc > 2 } {
  for {set i 2} {$i < $::argc} {incr i} {
      if {$i == 2} {
        set project_name [lindex $::argv $i]
      }
  }
} else {
  puts "Argument error. The project name must be an argument\n"
  exit
}

################################################################################
# Variables
################################################################################

set Solution ${::env(SONAR_PART_FAMILY)}
set Device ${::env(SONAR_PART)}
set Flow ""
set Clock 4.0
set DefaultFlag 1

set base_path BASE_PATH

set src_dir $base_path/src
set test_dir $base_path/testbench/build
set local_include -I$base_path/include
append include $local_include

################################################################################
# Body
################################################################################

# Project settings
open_project $project_name -reset

# Add the file for synthesis
add_files $src_dir/$project_name.cpp -cflags $include

# Add testbench files for co-simulation
add_files -tb  $test_dir/${project_name}/${project_name}_tb.cpp -cflags $include

# Set top module of the design
set_top $project_name

# Solution settings
open_solution -reset $Solution

# Set module prefix
config_rtl -encoding auto -prefix ${project_name}_ -reset all -reset_level low

# Add library
set_part $Device

# Set the target clock period
create_clock -period $Clock

################################################################################
# C Sim
################################################################################
#csim_design

################################################################################
# Synthesis
################################################################################
csynth_design

################################################################################
# Cosim
################################################################################
#cosim_design -rtl verilog -trace_level all

################################################################################
# Implementation
################################################################################
export_design -format ipxact

exit
