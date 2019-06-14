# This defines the input signals for an interface master
master_input_channels = {
    "tready": {"size": 1, "required": False}
}
# TODO enforce size checking and requirements
# This defines the output signals for an interface master
master_output_channels = {
    "tdata": {"size": 0, "required": True},
    "tvalid": {"size": 1, "required": True},
    "tlast": {"size": 1, "required": False},
    "tkeep": {"size": 0, "required": False},
    "tdest": {"size": 0, "required": False}
}

# Defines the systemverilog commands to use for a master/slave command. 
# - $$name can be used to refer to the interface name.
# - To refer to any signals, use args[x] where x is the channel's index as 
# defined in sv_args below.
# - To repeat a command for a set of channels, use a dict to list which channels,
# and use $$channel to substitute the name. $$i is used to refer to the channel's
# index in sv_args.
slave_action = [
    "@(posedge $$clock iff $$name_tready && $$name_tvalid);",
    "assert($$name_tdata == args[0]) begin",
    "end else begin",
    "    $error(\"AXI-S Assert failed at %t on $$name_tdata. Expected: %h, Received: %h\", $time, args[0], $$name_tdata);",
    "    error = 1'b1;",
    "    $stop;",
    "end"
]

master_action = [
    "wait($$clock == 0);",
    {"channels": {"tdata", "tlast", "tkeep", "tdest"}, "commands": ["$$name_$$channel = args[$$i];"]},
    "$$name_tvalid = 1'b1;",
    "@(posedge $$clock iff $$name_tready === 1'b1);",
    "@(negedge $$clock);",
    "$$name_tvalid = 1'b0;"
]

# These array define what signals should be printed out to the data file
# Arrays are needed to enforce that the data is written in the same order 
# every time.

sv_args = [
    "tdata",
    "tlast",
    "tkeep",
    "tdest"
]

c_args = [
    "tdata",
    "tlast",
    "tkeep",
    "tdest"
]

# defines an empty JSON structural object that is used as a template when writing
json_struct = {"type": "axis", "interface": "", "width": 0, "id": "", \
    "c_stream": "", "payload": []}

# this function defines operations (if any) that should be performed at any keys
# in the top level of the JSON struct object. If none, just use pass
def json_top(json_struct, interface):
    for channel in interface['channels']:
        if channel['type'] == 'tdata':
            json_struct['width'] = channel['size']

    if 'c_stream' in interface:
        json_struct['c_stream'] = interface['c_stream']

    return json_struct

# this function defines operations (if any) that should be performed at any keys
# in the payload of the JSON struct object. If none, just use pass
def json_payload(payload):
    if 'tdata' not in payload: #this is a loop
        newDataSeq2 = []
        for packet in payload['loop']['body']:
            packet2 = json_payload(packet)
            newDataSeq2.append(packet2)
        payload['loop']['body'] = newDataSeq2
        return payload
    else:
        if 'tkeep' not in payload:
            payload['tkeep'] = "KEEP_ALL"
        if 'callTB' not in payload:
            payload['callTB'] = 0
        if 'tlast' not in payload:
            payload['tlast'] = 0
        if 'tdest' not in payload:
            payload['tdest'] = 0
        return payload

# This function is called by parse to resolve any macros or strings that remain
# and turn them into ints
def convert(packet):
    if 'type' in packet:
        for word in packet['payload']:
            if 'tkeep' in word and not isinstance(word['tkeep'], (int, long)):
                if word['tkeep'] == "KEEP_ALL":
                    word['tkeep'] = (2 ** (packet['width'] / 8)) - 1
    else:
        for packet2 in packet:
            convert(packet2)

# This function is called by parse to count the number of packets in the payload 
# that will be written to the data file. This function should describe how packets
# should be counted (and if any should be ignored [i.e. if they are for CSIM])
def count(packet):
    svPacket = 0
    for payload in packet['payload']:
        if isinstance(payload['tdata'], (int, long)):
            svPacket += 1
        elif not payload['tdata'].startswith("0s"):
            svPacket += 1
    return svPacket

# These functions are used to write a line for the C and SV data files.

def write_sv(packet):
    line = ""
    for word in packet['payload']:
        if word['tkeep'] != 0: #exclude debug statements
            line += packet['type'] + " " + packet['interface']+ " " + str(len(sv_args))
            for arg in sv_args:
                line += " " + str(word[arg])
            line += "\n"
    return line[:-1]

def write_c(packet):
    line = ""
    for word in packet['payload']:
        line += packet['interface']+ " " + str(word['id']) + " " + \
            str(packet['c_stream']) + " " + str(len(c_args)) + " " + \
            str(word['callTB'])
        for arg in c_args:
            line += " " + str(word[arg])
        line += "\n"
    return line

def c_interface_in(tb_str, prev_str, interface, indent, tabSize):
    if tb_str != "":
        tb_str += indent + "else "
    if prev_str != "" and tb_str == "":
        tb_str += "else "
    tb_str += "if(!strcmp(interfaceType,\"" + interface['name'] + \
        "\")){\n"
    tb_str += indent + tabSize + "WRITE(" + \
        "" + interface['c_stream'] + ", " + interface['c_struct'] + ", " + \
        interface['name'] + ")\n"
    tb_str += indent + "}\n"
    return tb_str

def c_interface_out(tb_str, prev_str, interface, indent, tabSize):
    if tb_str != "":
        tb_str += indent + "else "
    if prev_str != "" and tb_str == "":
        tb_str += "else "
    tb_str += "if(!strcmp(interfaceType,\"" + interface['name'] + \
        "\")){\n"
    tb_str += indent + tabSize + "read = true;\n"
    tb_str += indent + tabSize + "READ(" + \
        "" + interface['c_stream'] + ", " + interface['c_struct'] + ", " + \
        interface['name'] + ")\n"
    tb_str += indent + "}\n"
    return tb_str

# Not currently used or supported
# interface = {"name": "axi_stream", "parameters": ["tdata"]}
# slave_bridge = "axis_m"
# master_bridge = "axis_s"
