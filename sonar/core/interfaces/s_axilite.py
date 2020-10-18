import os

# This defines the input signals for an interface master
master_input_channels = {
    "awready": {"size": 1, "required": True},
    "wready": {"size": 1, "required": True},
    "arready": {"size": 1, "required": True},
    "rvalid": {"size": 1, "required": True},
    "rdata": {"size": 0, "required": True},
    "rresp": {"size": 2, "required": True},
    "bvalid": {"size": 1, "required": True},
    "bresp": {"size": 2, "required": True},
}
# TODO enforce size checking and requirements
# This defines the output signals for an interface master
master_output_channels = {
    "awvalid": {"size": 1, "required": True},
    "awaddr": {"size": 0, "required": True},
    "wvalid": {"size": 1, "required": True},
    "wdata": {"size": 0, "required": True},
    "wstrb": {"size": 0, "required": True},
    "arvalid": {"size": 1, "required": True},
    "araddr": {"size": 0, "required": True},
    "rready": {"size": 1, "required": True},
    "bready": {"size": 1, "required": True},
}

# Defines the systemverilog commands to use for a master/slave command.
# - $$name can be used to refer to the interface name.
# - To refer to any signals, use args[x] where x is the channel's index as
# defined in sv_args below.
# - To repeat a command for a set of channels, use a dict to list which channels,
# and use $$channel to substitute the name. $$i is used to refer to the channel's
# index in sv_args.
# TODO resolve sv_arg indices here instead of using literals
slave_action = [
    "$$agent.AXI4LITE_READ_BURST(args[0],0,$$readData,$$readResp); //addr, prot, read_data, resp",
    "assert($$readData == args[1]) begin",
    "end else begin",
    '    $error("S-AXILITE Assert failed at %t on $$readData. Expected: %h, Received: %h", $time, args[1], $$readData);',
    "    error = 1'b1;",
    "    $stop;",
    "end",
]

master_action = ["$$agent.AXI4LITE_WRITE_BURST(args[0],0,args[1],$$writeResp);"]

# These array define what signals should be printed out to the data file
# Arrays are needed to enforce that the data is written in the same order
# every time.

sv_args = ["addr", "data", "mode"]

c_args = ["addr", "data"]

sv_interface_io = [
    {"mode": 0, "func": "slave_action", "arg": 2},
    {"mode": 1, "func": "master_action", "arg": 2},
]

# defines an empty JSON structural object that is used as a template when writing
json_struct = {
    "type": "s_axilite",
    "interface": "",
    "width": 0,
    "id": "",
    "payload": [],
}


def import_packages_global():
    imports = ""

    # versionInfo = subprocess.check_output("vivado -version", shell=True)
    version = os.getenv("SONAR_CAD_VERSION")
    # version = versionInfo.split()[1].decode("utf-8")

    if version == "2017.2":
        imports += "import axi_vip_v1_0_2_pkg::*;\n"
        return imports
    else:
        imports += "import axi_vip_pkg::*;\n"
        return imports


def import_packages_local(interface):
    return "import vip_bd_" + str(interface.index) + "_axi_vip_0_0_pkg::*;\n" 


# this function defines operations (if any) that should be performed at any keys
# in the top level of the YAML interface definition in the DUT
def yaml_top(interface):
    for channel in interface["channels"]:
        if channel["type"] == "wdata" or channel["type"] == "rdata":
            interface["dataWidth"] = channel["size"]
        if channel["type"] == "awaddr" or channel["type"] == "araddr":
            if channel["size"] < 12:
                channel["size"] = 12  # Required by AXI standard for 4K memory
            interface["addrWidth"] = channel["size"]

    if "readResp" not in interface:
        interface["readResp"] = "rresp_" + str(interface["index"])
    if "writeResp" not in interface:
        interface["writeResp"] = "wresp_" + str(interface["index"])
    if "readData" not in interface:
        interface["readData"] = "rdata_" + str(interface["index"])
    if "agent" not in interface:
        interface["agent"] = "master_agent_" + str(interface["index"])

    return interface


def initial_prologue(prologue, interface, indent):
    if prologue != "":
        prologue += indent
    prologue += (
        '$$agent = new("master vip agent", vip_bd_$$index_i.axi_vip_0.inst.IF);\n'
    )
    prologue += indent + '$$agent.set_agent_tag("$$agent");\n'
    prologue += indent + "$$agent.start_master();\n"
    return prologue


def exerciser_prologue(prologue, interface, indent):
    if prologue != "":
        prologue += indent
    prologue += "logic [$$dataWidth-1:0] rdata_$$index;\n"
    prologue += indent + "xil_axi_resp_t rresp_$$index;\n"
    prologue += indent + "xil_axi_resp_t wresp_$$index;\n"
    prologue += indent + "vip_bd_$$index_axi_vip_0_0_mst_t master_agent_$$index;\n"
    return prologue


def source_tcl(interface, path):

    tclFileName = os.path.join(os.path.dirname(__file__), "s_axilite_vip.tcl")
    # getFilePath("env", "SONAR_PATH", "/include/interfaces/s_axilite_vip.tcl")
    if tclFileName is None:
        exit(1)
    with open(tclFileName) as f:
        tclFile = f.read()
        tclFile = tclFile.replace("#DESIGN_NAME#", "vip_bd_" + str(interface.index))
        tclFile = tclFile.replace("#ADDR_WIDTH#", str(interface.addrWidth))
        tclFile = tclFile.replace("#DATA_WIDTH#", str(interface.dataWidth))
        tclFile = tclFile.replace("#ADDRESS#", str(interface.addr_range))
        tclFile = tclFile.replace("#ADDRESS_OFFSET#", str(interface.addr_offset))
        tclFile_gen = open(
            os.path.join(path, "s_axilite_vip_" + str(interface.index) + ".tcl"), "w+"
        )
        tclFile_gen.write(tclFile)
        tclFile_gen.close()


def instantiate(ip_inst, interface, indent, tabSize):
    index = str(interface.index)
    oneTab = indent + tabSize
    if ip_inst != "":
        ip_inst += indent
    ip_inst += "vip_bd_" + index + " vip_bd_" + index + "_i(\n"
    ip_inst += oneTab + ".aclk(" + interface.clock + "),\n"
    ip_inst += oneTab + ".aresetn(" + interface.reset + "),\n"
    for channels in (master_input_channels, master_output_channels):
        for channel in channels:
            ip_inst += (
                oneTab
                + ".m_axi_"
                + channel
                + "("
                + interface.name
                + "_"
                + channel
                + "),\n"
            )
    ip_inst = ip_inst[:-2] + "\n" + indent + ");\n"
    return ip_inst


# this function defines operations (if any) that should be performed at any keys
# in the top level of the JSON struct object. If none, just return json_struct
def json_top(json_struct, interface):
    json_struct["width"] = interface.dataWidth
    return json_struct


# this function defines operations (if any) that should be performed at any keys
# in the payload of the JSON struct object. If none, just return payload
def json_payload(payload):
    if "loop" in payload:  # this is a loop
        newDataSeq2 = []
        for packet in payload["loop"]["body"]:
            packet2 = json_payload(packet)
            newDataSeq2.append(packet2)
        payload["loop"]["body"] = newDataSeq2
        return payload
    else:
        # if "callTB" not in payload:
        #     payload["callTB"] = 0
        return payload


# This function is called by parse to resolve any macros or strings that remain
# and turn them into ints
def convert(packet):
    pass


# This function is called by parse to count the number of packets in the payload
# that will be written to the data file. This function should describe how packets
# should be counted (and if any should be ignored [i.e. if they are for other
# languages])
def count(packet):
    svPacket = len(packet["payload"])
    return svPacket


# These functions are used to write a line for the C and SV data files.


def write_sv(packet):
    line = ""
    for word in packet["payload"]:
        line += packet["type"] + " " + packet["name"] + " " + str(len(sv_args))
        for arg in sv_args:
            line += " " + str(word[arg])
        line += "\n"
    return line[:-1]


def write_c(packet):
    line = ""
    for word in packet["payload"]:
        line += (
            packet["name"]
            + " "
            + "NULL"
            + " "
            + "NULL"
            + " "
            + str(len(c_args))
            # + " "
            # + str(word["callTB"])
        )
        for arg in c_args:
            line += " " + str(word[arg])
        line += "\n"
    return line[:-1]


# def c_interface_in(tb_str, prev_str, interface, indent, tabSize):
#     if tb_str != "":
#         tb_str += indent + "else "
#     if prev_str != "" and tb_str == "":
#         tb_str += "else "
#     tb_str += 'if(!strcmp(interfaceType,"' + interface["name"] + '")){\n'
#     for idx, addr in enumerate(interface["addresses"]):
#         tb_str += indent + tabSize + "if(args[0] == " + str(addr) + "){\n"
#         tb_str += (
#             indent + tabSize + tabSize + interface["registers"][idx] + " = args[1];\n"
#         )
#         tb_str += indent + tabSize + "}\n"

#     tb_str += indent + "}\n"
#     return tb_str

c_interface_in = [
    {
        "foreach": "registers",
        "commands": ["if(args[0] == $$addresses){", "    $$registers = args[1];", "}"],
    },
]


def c_interface_out(tb_str, interface, indent, tabSize):
    return tb_str


# Not currently used or supported
# interface = {"name": "axi_stream", "parameters": ["tdata"]}
# slave_bridge = "axis_m"
# master_bridge = "axis_s"
