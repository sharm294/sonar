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

namespace eval 2017_2 {

proc create_VIP {bd_name addr_width data_width address address_offset} {
  
  set design_name $bd_name
  
  set result [get_design_name $design_name]

  set cur_design [lindex $result 0]
  set design_name [lindex $result 1]
  set errMsg [lindex $result 2]
  set nRet [lindex $result 3]

  if { $nRet != 0 } {
    catch {common::send_msg_id "BD_TCL-114" "ERROR" $errMsg}
    return $nRet
  }

  set parentCell [get_bd_cells /]

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
    catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent 
      cell <$parentCell>!"}
    return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
    catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has \
      TYPE = <$parentType>. Expected to be <hier>."}
    return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create interface ports
  set m_axi [ create_bd_intf_port -mode Master -vlnv \
    xilinx.com:interface:aximm_rtl:1.0 m_axi ]
  set_property -dict [ list \
    CONFIG.ADDR_WIDTH "$addr_width" \
    CONFIG.DATA_WIDTH "$data_width" \
    CONFIG.HAS_BURST {0} \
    CONFIG.HAS_CACHE {0} \
    CONFIG.HAS_LOCK {0} \
    CONFIG.HAS_PROT {0} \
    CONFIG.HAS_QOS {0} \
    CONFIG.HAS_REGION {0} \
    CONFIG.PROTOCOL {AXI4LITE} \
  ] $m_axi

  # Create ports
  set aclk [ create_bd_port -dir I -type clk aclk ]
  set_property -dict [ list \
    CONFIG.ASSOCIATED_BUSIF {m_axi} \
  ] $aclk
  set aresetn [ create_bd_port -dir I -type rst aresetn ]

  # Create instance: axi_vip_0, and set properties
  set axi_vip_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_vip:1.0 \
    axi_vip_0 ]
  set_property -dict [ list \
    CONFIG.ADDR_WIDTH "$addr_width" \
    CONFIG.ARUSER_WIDTH {0} \
    CONFIG.AWUSER_WIDTH {0} \
    CONFIG.BUSER_WIDTH {0} \
    CONFIG.DATA_WIDTH "$data_width" \
    CONFIG.HAS_BRESP {1} \
    CONFIG.HAS_BURST {0} \
    CONFIG.HAS_CACHE {0} \
    CONFIG.HAS_LOCK {0} \
    CONFIG.HAS_PROT {0} \
    CONFIG.HAS_QOS {0} \
    CONFIG.HAS_REGION {0} \
    CONFIG.HAS_RRESP {1} \
    CONFIG.HAS_WSTRB {1} \
    CONFIG.ID_WIDTH {0} \
    CONFIG.INTERFACE_MODE {MASTER} \
    CONFIG.PROTOCOL {AXI4LITE} \
    CONFIG.READ_WRITE_MODE {READ_WRITE} \
    CONFIG.RUSER_BITS_PER_BYTE {0} \
    CONFIG.RUSER_WIDTH {0} \
    CONFIG.SUPPORTS_NARROW {0} \
    CONFIG.WUSER_BITS_PER_BYTE {0} \
    CONFIG.WUSER_WIDTH {0} \
  ] $axi_vip_0

  # Create interface connections
  connect_bd_intf_net -intf_net axi_vip_0_M_AXI [get_bd_intf_ports m_axi] \
    [get_bd_intf_pins axi_vip_0/M_AXI]

  # Create port connections
  connect_bd_net -net aclk_1 [get_bd_ports aclk] \
    [get_bd_pins axi_vip_0/aclk]
  connect_bd_net -net aresetn_1 [get_bd_ports aresetn] \
    [get_bd_pins axi_vip_0/aresetn]

  # Create address segments
  create_bd_addr_seg -range $address -offset $address_offset \
    [get_bd_addr_spaces axi_vip_0/Master_AXI] \
    [get_bd_addr_segs m_axi/Reg] SEG_M_AXI_Reg

  generate_target Simulation [get_files $bd_name.bd]
  export_ip_user_files -of_objects [get_files $bd_name.bd] -no_script -force -quiet

  # Restore current instance
  current_bd_instance $oldCurInst

  save_bd_design
  close_bd_design [get_bd_designs $bd_name]
}

}

################################################################
# Check if script is running in correct Vivado version.
################################################################
set current_vivado_version [version -short]

if { [string first 2017.2 $current_vivado_version] != -1 } {
  2017_2::create_VIP #DESIGN_NAME# #ADDR_WIDTH# #DATA_WIDTH# #ADDRESS# #ADDRESS_OFFSET#
} else {
  puts ""
  catch {common::send_msg_id "BD_TCL-109" "WARNING" "Unsupported Vivado version:\
    $current_vivado_version for AXI VIP for s_axilite interface"}
  2017_2::create_VIP #DESIGN_NAME# #ADDR_WIDTH# #DATA_WIDTH# #ADDRESS# #ADDRESS_OFFSET#
  return 1
}
