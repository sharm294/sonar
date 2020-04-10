################################################################################
# Help
################################################################################

variable script_file
set script_file generate

proc help {} {
  puts "\nDescription:"
  puts "Recreate a Vivado project from this script. The created project will be"
  puts "functionally equivalent to the original project for which this script"
  puts "was generated. The script contains commands for creating a project,"
  puts "filesets, runs, adding/importing sources and setting properties on"
  puts "various objects.\n"
  puts "Syntax:"
  puts "$script_file -tclargs --project <name> \[--sim <type>\]"
  puts "$script_file -tclargs --help\n"
  puts "Usage:"
  puts "Name                   Description"
  puts "---------------------------------------------------------------------"
  puts "--project <name>       The name of the project to create. This must"
  puts "                         must match the name of an existing module"
  puts "--sim <type>           Automatically launch the simulation. Type must"
  puts "                         be one of: behav"
  puts "\[--help\]             Print help information for this script"
  puts "---------------------------------------------------------------------\n"
  exit 0
}

################################################################################
# Parse Arguments
################################################################################

set project_name foo

if { $::argc > 0 } {
  for {set i 0} {$i < $::argc} {incr i} {
      set option [string trim [lindex $::argv $i]]
      switch -regexp -- $option {
        "--project" { incr i; set project_name [lindex $::argv $i] }
        default {
            puts "ERROR: Unknown option '$option' specified, please type"
            puts "'$script_file -tclargs --help' for usage info.\n"
            return 1
        }
      }
  }
} else {
  puts "Argument error. Use '$script_file -tclargs --help' for usage info.\n"
  return 1
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
set global_include
append include $local_include " " $global_include

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
