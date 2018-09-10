import os
import sys
import yaml
import json
import datetime
import re
import copy

from utilities import getFilePath
from utilities import printError
from generate import generate

#TODO error handling
#TODO make seek size programmatic
#TODO add comments
#TODO clean up code and add functions
def generate_tb(mode, modeArg, filepath):
    userFileName = getFilePath(mode, modeArg, filepath)
    if userFileName is None:
        exit(1)

    pathTuple = os.path.split(userFileName)
    buildPath = pathTuple[0] + "/build/"
    if not os.path.exists(buildPath):
        os.makedirs(buildPath)
    dataFileName = buildPath + pathTuple[1].replace('.yaml', '.json')
    tbFileName_sv = buildPath + pathTuple[1].replace('.yaml', '_tb.sv')

    templateTB_sv = getFilePath("env", "SHOAL_SHARE_PATH", "/testbench/template_tb.sv")

    dataFile = open(dataFileName, "w+")
    yamlFile = open(userFileName, "r")
    with open(templateTB_sv, "r") as templateFile:
        templateTB_sv_str = templateFile.read()
    tbFile_sv = open(tbFileName_sv, "w+")

    yamlData = yaml.load(yamlFile)

    tbMetadataTags = ["Company","Engineer","Project_Name","Target_Devices","Tool_Versions", \
        "Description","Dependencies","Module_Name","Timescale"]

    for tbMetadataTag in tbMetadataTags:
        if yamlData[tbMetadataTag] is None:
            replaceStr = ""
        else:
            replaceStr = yamlData[tbMetadataTag].replace("_", " ")
        searchStr = "#" + tbMetadataTag.upper() + "#"
        templateTB_sv_str = templateTB_sv_str.replace(searchStr, replaceStr)

    templateTB_sv_str = templateTB_sv_str.replace("#CURR_DATE#", str(datetime.datetime.now()))
    templateTB_sv_str = templateTB_sv_str.replace("#DATA_FILE#", "\"" + yamlData['Module_Name']+"_sv.dat\"")

    #DUT perspective
    clocks_in = []
    axis_interfaces_in = []
    axis_interfaces_out = []
    signals_in = []
    signals_out = []

    tabSize = "    "

    for port in yamlData['DUT']:
        if 'type' in port:
            if port['type'] == "clock" and port['direction'] == "input":
                portCopy = port.copy()
                if 'size' not in portCopy:
                    portCopy['size'] = 1
                del portCopy['type']
                clocks_in.append(portCopy)
            elif port['type'] == "axis":
                portCopy = port.copy()
                for interface in portCopy['interface']:
                    if 'size' not in interface:
                        interface['size'] = 1
                del portCopy['type']
                if portCopy['direction'] == "slave":
                    axis_interfaces_in.append(portCopy)
                else:
                    axis_interfaces_out.append(portCopy)
            else:
                printError(1, "Unknown port type: " + port['type'])
                exit(1)
        else:
            portCopy = port.copy()
            if 'size' not in portCopy:
                portCopy['size'] = 1
            if portCopy['direction'] == "input":
                signals_in.append(portCopy)
            else:
                signals_out.append(portCopy)

    waitConditions = []
    for condition in yamlData['Wait_Conditions']:
        waitConditions.append(condition.copy())

    exerciserPorts = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#EXERCISER_PORTS#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    for index, clock in enumerate(clocks_in):
        if index != 0:
            exerciserPorts += leading_spaces
        exerciserPorts += "output logic " + clock['name'] + ",\n"
    for axis_in in axis_interfaces_in:
        exerciserPorts += leading_spaces + "axi_stream.axis_m_mp " + axis_in['name'].upper() + ",\n"
    for axis_out in axis_interfaces_out:
        exerciserPorts += leading_spaces + "axi_stream.axis_s_mp " + axis_out['name'].upper() + ",\n"
    for signal in signals_in:
        exerciserPorts += leading_spaces + "output logic " + signal['name'] + ",\n"
    for signal in signals_out:
        exerciserPorts += leading_spaces + "input wire " + signal['name'] + ",\n"
    templateTB_sv_str = templateTB_sv_str.replace("#EXERCISER_PORTS#", exerciserPorts[:-2])

    ifelse_signal = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#IF_ELSE_SIGNAL#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    for signal in signals_in:
        if ifelse_signal == "":
            ifelse_signal += "if(interfaceType_par == \"" + signal['name'] + "\") begin\n" + \
                leading_spaces + tabSize + signal['name'] + " = tdata;\n" + \
                leading_spaces + "end\n"
        else:
            ifelse_signal += leading_spaces + "else if(interfaceType_par == \"" + signal['name'] + "\") begin\n" + \
                leading_spaces + tabSize + signal['name'] + " = tdata;\n" + \
                leading_spaces + "end\n"
        exerciserPorts += leading_spaces + "output logic " + signal['name'] + ",\n"
    for axis_in in axis_interfaces_in:
        for interface in axis_in['interface']:
            if interface['type'] == "tdata" or interface['type'] == "tlast" or interface['type'] == "tvalid":
                if ifelse_signal == "":
                    ifelse_signal += "if(interfaceType_par == \""
                else:
                    ifelse_signal += leading_spaces + "else if(interfaceType_par == \""
                ifelse_signal += axis_in['name'] + "_" + interface['name'] + "\") begin\n" + \
                    leading_spaces + tabSize + axis_in['name'].upper() + "." + interface['type'] + " = tdata;\n" + \
                    leading_spaces + "end\n"
    for axis_in in axis_interfaces_out:
        for interface in axis_in['interface']:
            if interface['type'] == "tready":
                if ifelse_signal == "":
                    ifelse_signal += "if(interfaceType_par == \""
                else:
                    ifelse_signal += leading_spaces + "else if(interfaceType_par == \""
                ifelse_signal += axis_in['name'] + "_" + interface['name'] + "\") begin\n" + \
                    leading_spaces + tabSize + axis_in['name'].upper() + "." + interface['type'] + " = tdata;\n" + \
                    leading_spaces + "end\n"
    templateTB_sv_str = templateTB_sv_str.replace("#IF_ELSE_SIGNAL#", ifelse_signal[:-1])

    elseif_axisIn = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#ELSE_IF_AXIS_IN#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    for axis_in in axis_interfaces_in:
        if elseif_axisIn != "":
            elseif_axisIn += leading_spaces
        elseif_axisIn += "else if(interfaceType_par == \"" + axis_in['name'] + "\") begin\n"
        for interface in axis_in['interface']:
            if interface['type'] == "tdata" or interface['type'] == "tlast":
                elseif_axisIn += leading_spaces + tabSize + axis_in['name'].upper() + "." + interface['type'] + " = " + interface['type'] + ";\n"
        elseif_axisIn += leading_spaces + tabSize + axis_in['name'].upper() + ".tvalid = " + "1'b1;\n"
        elseif_axisIn += leading_spaces + tabSize + "@(posedge " + axis_in['clock'] + " iff " + axis_in['name'].upper() + ".tready);\n"
        elseif_axisIn += leading_spaces + tabSize + "@(posedge " + axis_in['clock'] + ");\n"
        elseif_axisIn += leading_spaces + tabSize + axis_in['name'].upper() + ".tvalid = " + "1'b0;\n"
        elseif_axisIn += leading_spaces + "end\n"
    templateTB_sv_str = templateTB_sv_str.replace("#ELSE_IF_AXIS_IN#", elseif_axisIn[:-1])

    elseif_axisOut = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#ELSE_IF_AXIS_OUT#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    for axis_out in axis_interfaces_out:
        if elseif_axisOut != "":
            elseif_axisOut += leading_spaces
        elseif_axisOut += "else if(interfaceType_par == \"" + axis_out['name'] + "\") begin\n"
        elseif_axisOut += leading_spaces + tabSize + "@(posedge " + axis_out['clock'] + " iff " + axis_out['name'].upper() + ".tready && " + \
            axis_out['name'].upper() + ".tvalid);\n"
        elseif_axisOut += leading_spaces + tabSize + "assert(" + axis_out['name'].upper() + ".tdata == tdata);\n"
        elseif_axisOut += leading_spaces + "end\n"
    templateTB_sv_str = templateTB_sv_str.replace("#ELSE_IF_AXIS_OUT#", elseif_axisOut[:-1])

    initial_clock = ""
    largestClock = ""
    largestPeriod = 0
    regex_int_str = re.compile("([0-9]+)([a-z]+)")
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#INITIAL_CLOCK#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    for clock in clocks_in:
        if initial_clock != "":
            initial_clock += leading_spaces
        initial_clock += "initial begin\n"
        initial_clock += leading_spaces + tabSize + clock['name'] + " = 0;\n"
        initial_clock += leading_spaces + tabSize + "forever begin\n"
        initial_clock += leading_spaces + tabSize + tabSize + "#(" + clock['period'] + "/2) " + \
            clock['name'] + " <= ~" + clock['name'] + ";\n"
        m = regex_int_str.match(clock['period'])
        if m.group(2) == "s":
            period = m.group(1) * 10 ** 15
        elif m.group(2) == "ms":
            period = m.group(1) * 10 ** 12
        elif m.group(2) == "us":
            period = m.group(1) * 10 ** 9
        elif m.group(2) == "ns":
            period = m.group(1) * 10 ** 6
        elif m.group(2) == "ps":
            period = m.group(1) * 10 ** 3
        else:
            period = m.group(1)
        if period > largestPeriod:
            largestPeriod = period
            largestClock = clock['name']
        initial_clock += leading_spaces + tabSize + "end\n"
        initial_clock += leading_spaces + "end\n"
    templateTB_sv_str = templateTB_sv_str.replace("#INITIAL_CLOCK#", initial_clock[:-1])
    templateTB_sv_str = templateTB_sv_str.replace("#VECTOR_CLOCK#", largestClock)

    tb_signal_list = ""
    maxSignalSize = 0
    maxAxisDataSize = 0
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#TB_SIGNAL_LIST#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    for clock in clocks_in:
        if tb_signal_list != "":
            tb_signal_list += leading_spaces
        tb_signal_list += "logic " + clock['name'] + ";\n"
    for signal in signals_in:
        if int(signal['size']) == 1:
           tb_signal_list += leading_spaces+ "logic " + signal['name'] + ";\n"
        else:
            tb_signal_list += leading_spaces+ "logic [" + str(int(signal['size']) - 1) + ":0] " + signal['name'] + ";\n"
        if int(signal['size']) > maxSignalSize:
            maxSignalSize = int(signal['size'])
    for signal in signals_out:
        if int(signal['size']) == 1:
           tb_signal_list += leading_spaces+ "logic " + signal['name'] + ";\n"
        else:
            tb_signal_list += leading_spaces + "logic [" + str(int(signal['size']) - 1) + ":0] " + signal['name'] + ";\n"
        if int(signal['size']) > maxSignalSize:
            maxSignalSize = int(signal['size'])
    for axis_in in axis_interfaces_in:
        for interface in axis_in['interface']:
            if int(interface['size']) == 1:
                tb_signal_list += leading_spaces+ "logic " + axis_in['name'] + "_" + interface['name'] + ";\n"
            else:
                tb_signal_list += leading_spaces + "logic [" + str(int(interface['size']) - 1) + ":0] " + axis_in['name'] + "_" + interface['name'] + ";\n"
            if int(interface['size']) > maxAxisDataSize and interface['type'] == "tdata":
                maxAxisDataSize = int(interface['size'])
    for axis_out in axis_interfaces_out:
        for interface in axis_out['interface']:
            if int(interface['size']) == 1:
                tb_signal_list += leading_spaces+ "logic " + axis_out['name'] + "_" + interface['name'] + ";\n"
            else:
                tb_signal_list += leading_spaces + "logic [" + str(int(interface['size']) - 1) + ":0] " + axis_out['name'] + "_" + interface['name'] + ";\n"
            if int(interface['size']) > maxAxisDataSize and interface['type'] == "tdata":
                maxAxisDataSize = int(interface['size'])
    templateTB_sv_str = templateTB_sv_str.replace("#TB_SIGNAL_LIST#", tb_signal_list[:-1])
    templateTB_sv_str = templateTB_sv_str.replace("#MAX_DATA_SIZE#", str(max(maxSignalSize, maxAxisDataSize)))
    templateTB_sv_str = templateTB_sv_str.replace("#MAX_KEEP_SIZE#", str(maxAxisDataSize/8))

    tb_axis_list = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#TB_AXIS_LIST#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    for axis_in in axis_interfaces_in:
        if tb_axis_list != "":
            tb_axis_list += leading_spaces
        for interface in axis_in['interface']:
            if interface['type'] == "tdata":
                tdataSize = interface['size']
        tb_axis_list += "axi_stream " + axis_in['name'] + "(\n"
        tb_axis_list += leading_spaces + tabSize + ".aclk(" + axis_in['clock'] + ")\n"
        tb_axis_list += leading_spaces + ");\n"
        tb_axis_list += leading_spaces + "axis_m #(\n" 
        tb_axis_list += leading_spaces + tabSize + ".DATA_WIDTH(" + str(tdataSize) + ")\n" 
        tb_axis_list += leading_spaces + ") " + axis_in['name'] + "_m(\n"
        tb_axis_list += leading_spaces + tabSize + ".AXIS_M(" + axis_in['name'] + "),\n"
        for interface in axis_in['interface']:
            tb_axis_list += leading_spaces + tabSize + "." + interface['type'] + "(" + axis_in['name'] + "_" + interface['name'] + "),\n"
        tb_axis_list = tb_axis_list[:-2] + "\n"
        tb_axis_list += leading_spaces + ");\n"
    for axis_out in axis_interfaces_out:
        if tb_axis_list != "":
            tb_axis_list += leading_spaces
        for interface in axis_out['interface']:
            if interface['type'] == "tdata":
                tdataSize = interface['size']
        tb_axis_list += "axi_stream " + axis_out['name'] + "(\n"
        tb_axis_list += leading_spaces + tabSize + ".aclk(" + axis_out['clock'] + ")\n"
        tb_axis_list += leading_spaces + ");\n"
        tb_axis_list += leading_spaces + "axis_s #(\n" 
        tb_axis_list += leading_spaces + tabSize + ".DATA_WIDTH(" + str(tdataSize) + ")\n" 
        tb_axis_list += leading_spaces + ") " + axis_out['name'] + "_s(\n"
        tb_axis_list += leading_spaces + tabSize + ".AXIS_S(" + axis_out['name'] + "),\n"
        for interface in axis_out['interface']:
            tb_axis_list += leading_spaces + tabSize + "." + interface['type'] + "(" + axis_out['name'] + "_" + interface['name'] + "),\n"
        tb_axis_list = tb_axis_list[:-2] + "\n"
        tb_axis_list += leading_spaces + ");\n"
    templateTB_sv_str = templateTB_sv_str.replace("#TB_AXIS_LIST#", tb_axis_list[:-1])

    exerciser_int = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#EXERCISER_INT#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    exerciser_int += "exerciser exerciser_i(\n"
    for index, clock in enumerate(clocks_in):
        exerciser_int += leading_spaces + tabSize + "." + clock['name'] + "(" + clock['name'] + "),\n"
    for axis_in in axis_interfaces_in:
        exerciser_int += leading_spaces + tabSize + "." + axis_in['name'].upper() + "(" + axis_in['name'] + "),\n"
    for axis_out in axis_interfaces_out:
        exerciser_int += leading_spaces + tabSize + "." + axis_out['name'].upper() + "(" + axis_out['name'] + "),\n"
    for signal in signals_in:
        exerciser_int += leading_spaces + tabSize + "." + signal['name'] + "(" + signal['name'] + "),\n"
    for signal in signals_out:
        exerciser_int += leading_spaces + tabSize + "." + signal['name'] + "(" + signal['name'] + "),\n"
    exerciser_int = exerciser_int[:-2] + "\n"
    exerciser_int += leading_spaces + ");\n"
    templateTB_sv_str = templateTB_sv_str.replace("#EXERCISER_INT#", exerciser_int[:-1])

    axis_assign = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#AXIS_ASSIGN#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    for axis_in in axis_interfaces_in:
        if axis_assign != "":
            axis_assign += leading_spaces
        axis_assign += axis_in['name'] + "_m.write();\n"
    for axis_out in axis_interfaces_out:
        if axis_assign != "":
            axis_assign += leading_spaces
        axis_assign += axis_out['name'] + "_s.read();\n"
    templateTB_sv_str = templateTB_sv_str.replace("#AXIS_ASSIGN#", axis_assign[:-1])

    dut_inst = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#DUT_INST#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    dut_inst += yamlData['Module_Name'] + " " + yamlData['Module_Name'] + "_i(\n"
    for clock in clocks_in:
        dut_inst += leading_spaces + tabSize + "." + clock['name'] + "(" + clock['name'] + "),\n"
    for signal in signals_in:
        dut_inst += leading_spaces + tabSize + "." + signal['name'] + "(" + signal['name'] + "),\n"
    for signal in signals_out:
        dut_inst += leading_spaces + tabSize + "." + signal['name'] + "(" + signal['name'] + "),\n"
    for axis_in in axis_interfaces_in:
        for interface in axis_in['interface']:
            dut_inst += leading_spaces + tabSize + "." + axis_in['name'] + "_" + interface['name'] + "(" + axis_in['name'] + "_" + interface['name'] + "),\n"
    for axis_out in axis_interfaces_out:
        for interface in axis_out['interface']:
            dut_inst += leading_spaces + tabSize + "." + axis_out['name'] + "_" + interface['name'] + "(" + axis_out['name'] + "_" + interface['name'] + "),\n"
    dut_inst = dut_inst[:-2] + "\n"
    dut_inst += leading_spaces + ");"
    templateTB_sv_str = templateTB_sv_str.replace("#DUT_INST#", dut_inst)
    # print(clocks_in)
    # print(axis_interfaces_in)
    # print(axis_interfaces_out)
    # print(signals)

    vectorNum = len(yamlData['Test_Vectors'])
    templateTB_sv_str = templateTB_sv_str.replace("#MAX_VECTORS#", str(vectorNum))

    parallelNum = 0
    json_dict = {}
    json_dict['data'] = []

    signal_json = {"type": "signal", "interface": "", "value": 0, "id": ""}
    axis_json = {"type": "axis", "interface": "", "width": 0, "id": "", "payload": []}

    #generate JSON file
    for vectorIndex, testVector in enumerate(yamlData['Test_Vectors']):
        if len(testVector['Test_Vector_' + str(vectorIndex)]) > parallelNum:
            parallelNum = len(testVector['Test_Vector_' + str(vectorIndex)])
        testVector_json = {}
        testVector_json['data'] = []
        json_dict['data'].append(testVector_json)
        for parallelIndex, parallelSection in enumerate(testVector['Test_Vector_' + str(vectorIndex)]):
            parallelSection_json = {}
            parallelSection_json['data'] = []
            testVector_json['data'].append(parallelSection_json)
            for packet in parallelSection['Parallel_Section_' + str(parallelIndex)]:
                delayCounter = 0
                axisCounter = 0
                timestampCounter = 0
                waitCounter = 0
                if 'macro' in packet:
                    if packet['macro'] == "INIT_SIGNALS":
                        for signal in signals_in:
                            cur_signal_json = copy.deepcopy(signal_json)
                            cur_signal_json['interface'] = signal['name']
                            cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + "_" + "init_" + signal['name']
                            parallelSection_json['data'].append(cur_signal_json)
                        for axis_in in axis_interfaces_in:
                            for interface in axis_in['interface']:
                                if interface['type'] == "tdata" or interface['type'] == "tlast" or interface['type'] == "tvalid":
                                    cur_signal_json = copy.deepcopy(signal_json)
                                    cur_signal_json['interface'] = axis_in['name'] + "_" + interface['name']
                                    cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + "_" + "init_" + cur_signal_json['interface']
                                    parallelSection_json['data'].append(cur_signal_json)
                        for axis_out in axis_interfaces_out:
                            for interface in axis_out['interface']:
                                if interface['type'] == "tready":
                                    cur_signal_json = copy.deepcopy(signal_json)
                                    cur_signal_json['interface'] = axis_out['name'] + "_" + interface['name']
                                    cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + "_" + "init_" + cur_signal_json['interface']
                                    parallelSection_json['data'].append(cur_signal_json)
                    elif packet['macro'] == "END":
                        cur_signal_json = copy.deepcopy(signal_json)
                        cur_signal_json['type'] = "end"
                        cur_signal_json['value'] = vectorIndex
                        cur_signal_json['interface'] = "Vector_" + str(vectorIndex)
                        cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + "_" + "end"
                        parallelSection_json['data'].append(cur_signal_json)
                elif 'delay' in packet:
                    m = regex_int_str.match(str(packet['delay']))
                    cur_signal_json = copy.deepcopy(signal_json)
                    cur_signal_json['type'] = 'delay'
                    cur_signal_json['interface'] = m.group(2)
                    cur_signal_json['value'] = m.group(1)
                    cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + "_" + "delay_" + str(delayCounter)
                    delayCounter += 1
                    parallelSection_json['data'].append(cur_signal_json)
                elif 'signal' in packet:
                    for signal in packet['signal']:
                        cur_signal_json = copy.deepcopy(signal_json)
                        cur_signal_json['interface'] = signal['name']
                        cur_signal_json['value'] = signal['value']
                        cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + "_" + "init_" + signal['name']
                        parallelSection_json['data'].append(cur_signal_json)
                elif 'timestamp' in packet:
                    cur_signal_json = copy.deepcopy(signal_json)
                    cur_signal_json['type'] = "timestamp"
                    cur_signal_json['interface'] = packet['timestamp']
                    cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + "_" + "timestamp_" + str(timestampCounter)
                    timestampCounter += 1
                    parallelSection_json['data'].append(cur_signal_json)
                elif 'wait' in packet:
                    cur_signal_json = copy.deepcopy(signal_json)
                    cur_signal_json['type'] = "wait"
                    cur_signal_json['interface'] = packet['wait']['key']
                    cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + "_" + "wait_" + str(waitCounter)
                    cur_signal_json['value'] = packet['wait']['value']
                    timestampCounter += 1
                    parallelSection_json['data'].append(cur_signal_json)
                elif 'axis' in packet:
                    cur_axis_json = copy.deepcopy(axis_json)
                    # print(json.dumps(cur_axis_json, indent=2))
                    cur_axis_json['interface'] = packet['axis']['name']
                    for axis_in in axis_interfaces_in:
                        if axis_in['name'] == cur_axis_json['interface']:
                            for interface in axis_in['interface']:
                                if interface['type'] == 'tdata':
                                    cur_axis_json['width'] = interface['size']
                    for axis_out in axis_interfaces_out:
                        if axis_out['name'] == cur_axis_json['interface']:
                            for interface in axis_out['interface']:
                                if interface['type'] == 'tdata':
                                    cur_axis_json['width'] = interface['size']
                    cur_axis_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + "_" + "axis_" + str(axisCounter) + "_"
                    axisCounter += 1
                    for payload in packet['axis']['payload']:
                        payloadCopy = payload.copy()
                        iterPayloadCopy = payloadCopy
                        while 'data' not in iterPayloadCopy:
                            iterPayloadCopy = iterPayloadCopy['body']                       
                        if 'keep' not in iterPayloadCopy:
                            if not isinstance(iterPayloadCopy['data'], (int, long)):
                                if iterPayloadCopy['data'].startswith("0s"):
                                    iterPayloadCopy['keep'] = 0
                                else:
                                    iterPayloadCopy['keep'] = "ALL"
                            else:
                                iterPayloadCopy['keep'] = "ALL"
                        if 'callTB' not in iterPayloadCopy:
                            iterPayloadCopy['callTB'] = 0
                        if 'last' not in iterPayloadCopy:
                            iterPayloadCopy['last'] = 0
                        cur_axis_json['payload'].append(iterPayloadCopy)
                    # print(json.dumps(cur_axis_json, indent=2))
                    parallelSection_json['data'].append(cur_axis_json.copy())

                # print(packet)

    if_else_wait = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#IF_ELSE_WAIT#" in line]
    leading_spaces = lineStr[0][:len(lineStr[0])-len(lineStr[0].lstrip())]
    for condition in waitConditions:
        if if_else_wait != "":
            if_else_wait += leading_spaces
        if_else_wait += "if(interfaceType_par == \"" + condition['key'] + "\") begin\n"
        conditionStr = condition['condition'].replace("$value", "tdata")
        if not conditionStr.endswith(";"):
            conditionStr += ";"
        if_else_wait += leading_spaces + tabSize + conditionStr + "\n"
        if_else_wait += leading_spaces + "end\n"
    templateTB_sv_str = templateTB_sv_str.replace("#IF_ELSE_WAIT#", if_else_wait[:-1])
                        
    templateTB_sv_str = templateTB_sv_str.replace("#MAX_PARALLEL#", str(parallelNum))
    json.dump(json_dict, dataFile, indent=2)

    tbFile_sv.write(templateTB_sv_str)

    dataFile.close()
    yamlFile.close()
    tbFile_sv.close()

    generate("absolute", None, dataFileName)

if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "-h" or arg == "--help":
            print("Usage: python generate_tb.py mode modeArg filename")
            print("  mode: env - use relative path from an environment variable")
            print("        path - use relative path from a string")
            print("        absolute - use absolute filepath")
            print("  modeArg: environment variable or path string. None otherwise")
            print("  filename: user file to read")

    if (len(sys.argv) == 4):
        generate_tb(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Incorrect number of arguments. Use -h or --help")