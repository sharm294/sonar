# This procedure is the default Vivado-generated procedure to obtain the design
# name. It returns a list of values for other procedures to use.
proc get_design_name {design_name} {
  set cur_design [current_bd_design -quiet]
  set list_cells [get_bd_cells -quiet]
  set errMsg ""
  set nRet 0

  if { ${design_name} eq "" } {
    # USE CASES:
    # 1): Missing design name
    set errMsg "Please set the variable <design_name> to a non-empty value."
    set nRet 1
  } elseif { ${cur_design} ne "" && ${list_cells} eq "" } {
    # USE CASES:
    # 2): Current design opened AND is empty AND names same.
    # 3): Current design opened AND is empty AND names diff; design_name NOT
    #     in project.
    # 4): Current design opened AND is empty AND names diff; design_name exists
    #     in project.

    if { $cur_design ne $design_name } {
      common::send_msg_id "BD_TCL-001" "INFO" "Changing value of \
        <design_name> from <$design_name> to <$cur_design> since current \
        design is empty."
      set design_name [get_property NAME $cur_design]
    }
    common::send_msg_id "BD_TCL-002" "INFO" "Constructing design in IPI design \
      <$cur_design>..."

  } elseif { ${cur_design} ne "" && $list_cells ne "" && \
    $cur_design eq $design_name } {
    # USE CASES:
    # 5) Current design opened AND has components AND same names.

    set errMsg "Design <$design_name> already exists in your project, please \
      set the variable <design_name> to another value."
    set nRet 1
  } elseif { [get_files -quiet ${design_name}.bd] ne "" } {
    # USE CASES:
    # 6) Current opened design, has components, but diff names, design_name
    #    exists in project.
    # 7) No opened design, design_name exists in project.
    set errMsg "Design <$design_name> already exists in your project, please \
      set the variable <design_name> to another value."
    set nRet 2
  } else {
    # USE CASES:
    #    8) No opened design, design_name not in project.
    #    9) Current opened design, has components, but diff names, design_name
    #       not in project.
    common::send_msg_id "BD_TCL-003" "INFO" "Currently there is no design \
      <$design_name> in project, so creating one..."

    create_bd_design $design_name

    common::send_msg_id "BD_TCL-004" "INFO" "Making design <$design_name> as \
      current_bd_design."
    current_bd_design $design_name
  }

  return [list $cur_design $design_name $errMsg $nRet]
}

proc get_full_ip_name {ip_name} {
  return [lindex [get_ipdefs] [lsearch [get_ipdefs] *$ip_name*]]
}

proc get_ip_version {ip_name} {
  return [lindex [split [lindex [get_ipdefs] [lsearch [get_ipdefs] *$ip_name*]] :] end]
}

proc check_ip {ip supported_versions} {
  set ip_version [get_ip_version $ip]
  if { [ lsearch $supported_versions $ip_version] != -1 } {
    set full_ip_name [get_full_ip_name $ip]
  } else {
    puts ""
    catch {common::send_msg_id "BD_TCL-109" "ERROR" "$ip either doesn't exist, \
      exists in the wrong version, or is too ambiguous. Supported versions of this
      IP are: $supported_versions"}
    set full_ip_name -1
  }
}

proc check_vivado_version {supported_versions mode} {
  set current_vivado_version [string range [version -short] 0 5]

  if { [ lsearch $supported_versions $current_vivado_version] != -1 } {
    return 0
  } else {
    puts ""
    catch {common::send_msg_id "BD_TCL-109" "$mode" "Using untested Vivado version\
      $current_vivado_version. If everything works as expected, consider adding\
      this version to the list of supported versions to remove this warning"}
    return 1
  }
}
