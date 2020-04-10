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

variable project_name
variable auto_sim
set auto_sim "0"
variable create_proj
set create_proj 0
set run_synth 0
set run_impl 0
set write_bit 0
set export_hw 0
set postscript ""

if { $::argc > 0 } {
  for {set i 0} {$i < $::argc} {incr i} {
    set option [string trim [lindex $::argv $i]]
    switch -regexp -- $option {
      "--project" { incr i; set project_name [lindex $::argv $i] }
      "--create" { incr i; set create_proj [lindex $::argv $i] }
      "--synth" { incr i; set run_synth [lindex $::argv $i] }
      "--impl" { incr i; set run_impl [lindex $::argv $i] }
      "--bit" { incr i; set write_bit [lindex $::argv $i] }
      "--export" { incr i; set export_hw [lindex $::argv $i] }
      "--sim" { incr i; set auto_sim [lindex $::argv $i] }
      "--postscript" { incr i; set postscript [lindex $::argv $i]}
      "--help" { help }
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

switch $auto_sim {
  "0" {set auto_sim 0}
  "behav" {set auto_sim 1}
  default {
    puts "ERROR: Unknown --sim option $auto_sim specified, please type"
    puts "'$script_file -tclargs --help' for usage info.\n"
    return 1
  }
}

################################################################################
# Include
################################################################################

source ${::env(SONAR_PATH)}/tcl/utilities.tcl

################################################################################
# Variables
################################################################################

variable part_name
set part_name ${::env(SONAR_PART)}

set $base_path BASE_PATH

# Set the reference directory for source file relative paths
set origin_dir $base_path/vivado
set src_dir $origin_dir/src/$project_name
set cad_ver ${::env(SONAR_CAD_VERSION)}

# Set the directory path for the original project from where this script was exported
set orig_proj_dir "[file normalize "$origin_dir/projects/$cad_ver/$part_name/$project_name"]"

# Set the directory path for the original project from where this script was exported
set orig_proj_dir "[file normalize "$origin_dir/build/vivado/sample"]"

################################################################################
# Body
################################################################################

if { $create_proj > 0 } {

  puts "Creating project..."

  # Create project
  create_project $project_name $orig_proj_dir -part $part_name -force

  # Set the directory path for the new project
  set proj_dir [get_property directory [current_project]]

  # Set project properties
  set obj [get_projects $project_name]
  set_property -name "default_lib" -value "xil_defaultlib" -objects $obj
  set_property -name "ip_cache_permissions" -value "read write" -objects $obj
  set_property -name "ip_output_repo" -value "$proj_dir/$project_name.cache/ip" -objects $obj
  set_property -name "part" -value "$part_name" -objects $obj
  if {[info exists env(SHOAL_BOARD)]} {
    if { [ lsearch [get_board_parts] ${::env(SHOAL_BOARD)}] != -1 } {
      set_property board_part ${::env(SHOAL_BOARD)} -objects $obj
    } else {
      puts ""
      catch {common::send_msg_id "BD_TCL-109" "ERROR" "${::env(SHOAL_BOARD)} \
        not found in this Vivado installation"
        return -1
      }
    }
  }
  set_property -name "sim.ip.auto_export_scripts" -value "1" -objects $obj
  set_property -name "simulator_language" -value "Mixed" -objects $obj

  # Read all source files for this module
  set all_files [glob -directory "$src_dir" *]

  # Create 'sources_1' fileset (if not found)
  if {[string equal [get_filesets -quiet sources_1] ""]} {
    create_fileset -srcset sources_1
  }

  # Set 'sources_1' fileset object
  set obj [get_filesets sources_1]
  # remove the tb file from the file set (it's added separately to the simset)
  if {! [catch {glob -directory "$src_dir" *_tb.sv} yikes] } {
    set files [listcomp $all_files [glob -directory "$src_dir" *_tb.sv] ]
    set TB_exists 1
  } else {
    set files $all_files
    set TB_exists 0
  }
  # if .tcl files exist, remove them as well
  if {! [catch {glob -directory "$src_dir" *.tcl} yikes] } {
    set files [listcomp $files [glob -directory "$src_dir" *.tcl] ]
  }
  # if waveform config files exist, remove them as well
  if {! [catch {glob -directory "$src_dir" *.wcfg} yikes] } {
    set files [listcomp $files [glob -directory "$src_dir" *.wcfg] ]
  }
  # add the remaining files to the sources set
  if {$files ne ""} {
    add_files -norecurse -fileset $obj $files
  }
  if {! [catch {glob -directory "$src_dir" *.dat} yikes] } {
    set data_files [glob -directory "$src_dir" *.dat]
    foreach dataFile $data_files {
      set file_obj [get_files -of_objects [get_filesets sources_1] [list "*$dataFile"]]
      set_property -name "file_type" -value "Data Files" -objects $file_obj
    }
  }

  # Set 'sources_1' fileset properties
  set obj [get_filesets sources_1]
  set_property -name "top" -value "$project_name" -objects $obj

  # Create 'constrs_1' fileset (if not found)
  if {[string equal [get_filesets -quiet constrs_1] ""]} {
    create_fileset -constrset constrs_1
  }

  # Create 'sim_1' fileset (if not found)
  if {[string equal [get_filesets -quiet sim_1] ""]} {
    create_fileset -simset sim_1
  }

  # Set 'sim_1' fileset object
  set obj [get_filesets sim_1]
  if {! [catch {glob -directory "$src_dir" *.wcfg} yikes] } {
    set files [glob -directory "$src_dir" *.wcfg]
    add_files -norecurse -fileset $obj $files
  }
  if {$TB_exists == 1} {
    set files [glob -directory "$src_dir" *_tb.sv]
    add_files -norecurse -fileset $obj $files

    # Set 'sim_1' fileset file properties for remote files
    foreach dataFile $files {
      set file_obj [get_files -of_objects [get_filesets sim_1] [list "*$dataFile"]]
      set_property -name "file_type" -value "SystemVerilog" -objects $file_obj
    }
  }

  # Set 'sim_1' fileset properties
  set obj [get_filesets sim_1]
  if {$TB_exists == 1} {
    set_property -name "top" -value "${project_name}_tb" -objects $obj
  }
  set_property -name "xsim.simulate.runtime" -value "-1" -objects $obj
  if {! [catch {glob -directory "$src_dir" *.wcfg} yikes] } {
    set_property -name "xsim.view" -value "${project_name}.wcfg" -objects $obj
  }

  if {! [catch {glob -directory "$src_dir" *.tcl} yikes] } {
    set files [glob -directory "$src_dir" *.tcl]
    foreach tclFile $files {
      source $tclFile -notrace
    }
  }

  # Create 'synth_1' run (if not found)
  if {[string equal [get_runs -quiet synth_1] ""]} {
    create_run -name synth_1 -part $part_name -flow {Vivado Synthesis 2017} \
    -strategy "Vivado Synthesis Defaults" -constrset constrs_1
  } else {
    set_property strategy "Vivado Synthesis Defaults" [get_runs synth_1]
    set_property flow "Vivado Synthesis 2017" [get_runs synth_1]
  }
  set obj [get_runs synth_1]
  set_property -name "needs_refresh" -value "1" -objects $obj
  set_property -name "part" -value "$part_name" -objects $obj

  # set the current synth run
  current_run -synthesis [get_runs synth_1]

  # Create 'impl_1' run (if not found)
  if {[string equal [get_runs -quiet impl_1] ""]} {
    create_run -name impl_1 -part $part_name -flow {Vivado Implementation 2017} \
      -strategy "Vivado Implementation Defaults" -constrset constrs_1 \
      -parent_run synth_1
  } else {
    set_property strategy "Vivado Implementation Defaults" [get_runs impl_1]
    set_property flow "Vivado Implementation 2017" [get_runs impl_1]
  }
  set obj [get_runs impl_1]
  set_property -name "part" -value "$part_name" -objects $obj
  set_property -name "steps.write_bitstream.args.readback_file" -value "0" \
    -objects $obj
  set_property -name "steps.write_bitstream.args.verbose" -value "0" \
    -objects $obj

  # set the current impl run
  current_run -implementation [get_runs impl_1]
} else {
  puts "Opening project..."

  open_project -part $part_name $orig_proj_dir/$project_name.xpr

  upgrade_ip [get_ips] -quiet

  if {$auto_sim > 0} {
    reset_target simulation [get_ips] -quiet
    export_ip_user_files -of_objects  [get_ips] -sync -no_script -force -quiet
  }
}

if {[file exists $src_dir/${project_name}_prologue.tcl]} {
  set tclFile $src_dir/${project_name}_prologue.tcl
  source $tclFile -notrace
}

if {$run_synth > 0} {
  reset_run synth_1
  launch_runs synth_1 -jobs 2
}

if {$run_impl > 0} {
  launch_runs impl_1 -jobs 2
}

if {$write_bit > 0} {
  launch_runs impl_1 -to_step write_bitstream -jobs 2
}

if {$export_hw > 0} {
  file mkdir $orig_proj_dir/$project_name.sdk
  file copy -force $orig_proj_dir/$project_name.runs/impl_1/${project_name}_bd_wrapper.sysdef \
    $orig_proj_dir/$project_name.sdk/${project_name}_bd_wrapper.hdf
}

if {$auto_sim > 0} {
  launch_simulation
}

if {! [string equal $postscript ""]} {
  source $postscript
}
