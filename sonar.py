import os
import sys
import json
import datetime
import re
import copy
import importlib
from shlex import split as quoteSplit

from utilities import getFilePath
from utilities import printError
from generate import generate

################################################################################
### writeJSONPacket ###
# This function converts a YAML command into its equivalent JSON.

def writeJSONPacket(parallelSection_json, packet, vectorIndex, parallelIndex, 
signals_in, signals_out, interface_in, interface_out, usedInterfaces):
    signal_json = {"type": "signal", "interface": "", "value": 0, "id": ""}
    regex_int_str = re.compile("([0-9]+)([a-z]+)")
    delayCounter = 0
    interfaceCounter = 0
    displayCounter = 0
    waitCounter = 0
    timestampCounter = 0
    if 'macro' in packet:
        if packet['macro'] == "INIT_SIGNALS":
            for signal in signals_in:
                cur_signal_json = copy.deepcopy(signal_json)
                cur_signal_json['interface'] = signal['name']
                cur_signal_json['id'] = str(vectorIndex) + "_" + \
                    str(parallelIndex) + "_" + "init_" + signal['name']
                parallelSection_json['data'].append(cur_signal_json)
            for interface in interface_in:
                currInterface = usedInterfaces[interface['type']]
                for channel in interface['channels']:
                    if channel['type'] in currInterface.master_output_channels:
                        cur_signal_json = copy.deepcopy(signal_json)
                        cur_signal_json['interface'] = interface['name'] + "_" \
                            + channel['name']
                        cur_signal_json['id'] = str(vectorIndex) + "_" + \
                            str(parallelIndex) + "_" + "init_" + \
                            cur_signal_json['interface']
                        parallelSection_json['data'].append(cur_signal_json)
            for interface in interface_out:
                currInterface = usedInterfaces[interface['type']]
                for channel in interface['channels']:
                    if channel['type'] in currInterface.master_input_channels:
                        cur_signal_json = copy.deepcopy(signal_json)
                        cur_signal_json['interface'] = interface['name'] + "_" \
                            + channel['name']
                        cur_signal_json['id'] = str(vectorIndex) + "_" + \
                            str(parallelIndex) + "_" + "init_" + \
                            cur_signal_json['interface']
                        parallelSection_json['data'].append(cur_signal_json)
        elif packet['macro'] == "END":
            cur_signal_json = copy.deepcopy(signal_json)
            cur_signal_json['type'] = "end"
            cur_signal_json['value'] = vectorIndex
            cur_signal_json['interface'] = "Vector_" + str(vectorIndex)
            cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) \
                + "_" + "end"
            parallelSection_json['data'].append(cur_signal_json)
    elif 'delay' in packet:
        m = regex_int_str.match(str(packet['delay']))
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json['type'] = 'delay'
        cur_signal_json['interface'] = m.group(2)
        cur_signal_json['value'] = m.group(1)
        cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + \
            "_" + "delay_" + str(delayCounter)
        delayCounter += 1
        parallelSection_json['data'].append(cur_signal_json)
    elif 'signal' in packet:
        for signal in packet['signal']:
            cur_signal_json = copy.deepcopy(signal_json)
            cur_signal_json['interface'] = signal['name']
            cur_signal_json['value'] = signal['value']
            cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) \
                + "_" + "init_" + signal['name']
            parallelSection_json['data'].append(cur_signal_json)
    elif 'display' in packet:
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json['type'] = "display"
        cur_signal_json['interface'] = "\"" + packet['display'] + "\""
        cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + \
            "_" + "display_" + str(displayCounter)
        displayCounter += 1
        parallelSection_json['data'].append(cur_signal_json)
    elif 'timestamp' in packet:
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json['type'] = "timestamp"
        cur_signal_json['interface'] = packet['timestamp']
        cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + \
            "_" + "timestamp_" + str(timestampCounter)
        timestampCounter += 1
        parallelSection_json['data'].append(cur_signal_json)
    elif 'flag' in packet:
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json['type'] = "flag"
        if "set_flag" in packet['flag']:
            cur_signal_json['interface'] = "set"
            cur_signal_json['value'] = packet['flag']['set_flag']
        else:
            cur_signal_json['interface'] = "clear"
            cur_signal_json['value'] = packet['flag']['clear_flag']
        cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + \
            "_" + "flag_" + str(timestampCounter)
        timestampCounter += 1
        parallelSection_json['data'].append(cur_signal_json)
    elif 'wait' in packet:
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json['type'] = "wait"
        cur_signal_json['interface'] = packet['wait']['key']
        cur_signal_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + \
            "_" + "wait_" + str(waitCounter)
        if 'value' in packet['wait']:
            cur_signal_json['value'] = packet['wait']['value']
        else:
            cur_signal_json['value'] = 0
        waitCounter += 1
        parallelSection_json['data'].append(cur_signal_json)
    elif 'interface' in packet:
        currInterface = usedInterfaces[packet['interface']['type']]
        cur_interface_json = copy.deepcopy(currInterface.json_struct)
        cur_interface_json['interface'] = packet['interface']['name']
        for interface in interface_in:
            if interface['name'] == cur_interface_json['interface']:
                cur_interface_json = currInterface.json_top(cur_interface_json, \
                    interface['channels'])
        for interface in interface_out:
            if interface['name'] == cur_interface_json['interface']:
                cur_interface_json = currInterface.json_top(cur_interface_json, \
                    interface['channels'])
        cur_interface_json['id'] = str(vectorIndex) + "_" + str(parallelIndex) + \
            "_" + interface['type'] + "_" + str(interfaceCounter) + "_"
        interfaceCounter += 1
        for payload in packet['interface']['payload']:
            payloadCopy = payload.copy()
            payloadCopy = currInterface.json_payload(payloadCopy)
            cur_interface_json['payload'].append(payloadCopy)
        parallelSection_json['data'].append(cur_interface_json.copy())
    else:
        printError(1, "Unknown packet type: ")
        print(packet)
        exit(1)

################################################################################
### writeJSON ###
# This function converts the YAML test vectors to JSON and calls any interface 
# specific functions to fill in the JSON structs
def writeJSON(testVectors, dataFile, signals_in, signals_out, interface_in, 
    interface_out, usedInterfaces):
    parallelNum = 0
    json_dict = {}
    json_dict['data'] = []

    #generate JSON file
    for vectorIndex, testVector in enumerate(testVectors):
        if len(testVector['Test_Vector_' + str(vectorIndex)]) > parallelNum:
            parallelNum = len(testVector['Test_Vector_' + str(vectorIndex)])
        testVector_json = {}
        testVector_json['data'] = []
        json_dict['data'].append(testVector_json)
        testVectorInst = testVector['Test_Vector_' + str(vectorIndex)]
        for parallelIndex, parallelSection in enumerate(testVectorInst):
            parallelSection_json = {}
            parallelSection_json['data'] = []
            testVector_json['data'].append(parallelSection_json)
            for packet in parallelSection['Parallel_Section_' + str(parallelIndex)]:
                writeJSONPacket(parallelSection_json, packet, vectorIndex, \
                    parallelIndex, signals_in, signals_out, interface_in, \
                    interface_out, usedInterfaces)
    
    json.dump(json_dict, dataFile, indent=2)
    return parallelNum

################################################################################
### getIndentation ###
# This function extracts the indentation level of a line

def getIndentation(textStr):
    return textStr[0][:len(textStr[0])-len(textStr[0].lstrip())]

################################################################################
### commandVarReplaceSub ###
# This function replaces any $variables with their corresponding key from the 
# YAML
def commandVarReplaceSub(elseif_interfaceIn, command, interface, indent):
    command = command.replace("$name", interface['name'])
    regex_variable = re.compile("\$\w+")
    for variable in re.findall(regex_variable, command):
        command = command.replace(variable, interface[variable[1:]])
    elseif_interfaceIn += indent + command + "\n"
    return elseif_interfaceIn

#This function replaces the variables in an interface action block. There are 
#two named variables: $name (referring to the interface name) and $channel (
#referring to a particular side channel). All other $ variables must be keys in
#the interface declaration in the configuration file
def commandVarReplace(elseif_interfaceIn, interface, actions, indent, args):
    for action in actions:
        #check if there is a command to repeat for a set of channels
        if isinstance(action, dict):
            for command in action['commands']:
                regex_channel = re.compile("\$channel")
                if re.findall(regex_channel, command): #if $channel in command
                    index = 0
                    for channel in interface['channels']:
                        if channel['type'] in action['channels']:
                            commandCopy = copy.deepcopy(command)
                            commandCopy = commandCopy.replace("$channel", 
                                channel['type'])
                            commandCopy = commandCopy.replace("$i",
                                str(args[channel['type']]))
                            index += 1
                            elseif_interfaceIn = commandVarReplaceSub(
                                elseif_interfaceIn, commandCopy, interface,
                                indent)
                else:
                    commandCopy = copy.deepcopy(command)
                    elseif_interfaceIn = commandVarReplaceSub(elseif_interfaceIn, 
                        commandCopy, interface, indent)
        else:
            commandCopy = copy.deepcopy(action)
            elseif_interfaceIn = commandVarReplaceSub(elseif_interfaceIn,
                commandCopy, interface, indent)

    return elseif_interfaceIn

################################################################################
### setFromConfig ###
#This function performs all the direct substititions from the configuration file 
#to the testbench file
def setFromConfig(templateTB_sv_str, yamlData):
    tbMetadataTags = ["Company","Engineer","Project_Name","Target_Devices",\
        "Tool_Versions", "Description","Dependencies","Module_Name","Timescale",\
        "Flag_Count"]

    for tbMetadataTag in tbMetadataTags:
        if yamlData[tbMetadataTag] is None:
            replaceStr = ""
        else:
            replaceStr = str(yamlData[tbMetadataTag]).replace("_", " ")
        searchStr = "#" + tbMetadataTag.upper() + "#"
        templateTB_sv_str = templateTB_sv_str.replace(searchStr, replaceStr)

    templateTB_sv_str = templateTB_sv_str.replace("#CURR_DATE#", \
        str(datetime.datetime.now()))
    templateTB_sv_str = templateTB_sv_str.replace("#DATA_FILE#", "\"" + \
        yamlData['Module_Name']+"_sv.dat\"")

    return templateTB_sv_str

#TODO error handling
#TODO make seek size programmatic
#TODO add comments
#TODO clean up code and add functions
################################################################################
### sonar ###
# This function uses a configuration file to generate testbenches, data for the 
# the testbenches to use, and a number of JSON files (for legacy reasons).
def sonar(mode, modeArg, filepath):

#------------------------------------------------------------------------------#
    # Open all the relevant files and make the simple text substitutions

    userFileName = getFilePath(mode, modeArg, filepath)
    if userFileName is None:
        exit(1)

    pathTuple = os.path.split(userFileName)
    configFile = open(userFileName, "r")
    if userFileName.endswith(".yaml"):
        import yaml
        yamlData = yaml.load(configFile)
        fileType = ".yaml"
    else:
        printError(1, "Unsupported configuration file")
        exit(1)

    buildPath = pathTuple[0] + "/build/"
    if not os.path.exists(buildPath):
        os.makedirs(buildPath)
    dataFileName = buildPath + pathTuple[1].replace(fileType, '.json')
    tbFileName_sv = buildPath + pathTuple[1].replace(fileType, '_tb.sv')
    tbFileName_c = buildPath + pathTuple[1].replace(fileType, '_tb.cpp')

    templateTB_sv = getFilePath("env", "SONAR_PATH", "/include/template_tb.sv")
    templateTB_c = getFilePath("env", "SONAR_PATH", "/include/template_tb.cpp")

    dataFile = open(dataFileName, "w+")
    
    with open(templateTB_sv, "r") as templateFile:
        templateTB_sv_str = templateFile.read()
    tbFile_sv = open(tbFileName_sv, "w+")

    with open(templateTB_c, "r") as templateFile:
        templateTB_c_str = templateFile.read()
    tbFile_c = open(tbFileName_c, "w+")

    # set the directly replaceable text into the testbench
    templateTB_sv_str = setFromConfig(templateTB_sv_str, yamlData)

    templateTB_c_str = templateTB_c_str.replace("#FUNCTION#", 
        yamlData['Module_Name'].upper())
    dataFile_c = dataFileName.replace(".json", "_c.dat")
    templateTB_c_str = templateTB_c_str.replace("#DATA_FILE#", "\"" + \
        dataFile_c + "\"")
    templateTB_c_str = templateTB_c_str.replace("#HEADER_FILE#", "\"" + \
        yamlData['Module_Name']+".hpp\"")

    #insert all the interface systemverilog definitions in the testbench
    usedInterfaces = {}
    include_interfaces = ""
    for interface in yamlData['Interfaces']:
        usedInterfaces[interface] = importlib.import_module("include." + \
            interface)
        include_interfaces += "`include \"" + interface + ".sv\"\n"

    # templateTB_sv_str = templateTB_sv_str.replace("#INCLUDE_INTERFACES#", 
    #     include_interfaces[:-1])

    vectorNum = len(yamlData['Test_Vectors'])
    templateTB_sv_str = templateTB_sv_str.replace("#MAX_VECTORS#", str(vectorNum))

#------------------------------------------------------------------------------#
    # Read configuration file into separate structures for easier access

    # Direction is relative to the DUT
    clocks_in = []
    signals_in = []
    signals_out = []
    interface_in = []
    interface_out = []

    tabSize = "    "

    for port in yamlData['DUT']:
        if 'type' in port:
            if port['type'] == "clock" and port['direction'] == "input":
                portCopy = port.copy()
                if 'size' not in portCopy:
                    portCopy['size'] = 1
                del portCopy['type']
                clocks_in.append(portCopy)
            elif port['type'] in usedInterfaces:
                portCopy = port.copy()
                for channel in portCopy['channels']:
                    if 'size' not in channel:
                        channel['size'] = 1
                if portCopy['direction'] == "slave":
                    interface_in.append(portCopy)
                else:
                    interface_out.append(portCopy)
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

    time_format = "$timeformat("
    with open(templateTB_sv,'r') as f:
        l = [line for line in f if "#TIME_FORMAT#" in line]
    leading_spaces = getIndentation(l)
    precision = str(yamlData['Time_Format']['precision'])
    timeFormat = yamlData['Time_Format']['unit']
    if timeFormat.endswith("fs"):
        time_format += "-15, " + precision + ", \" fs\", 0);"
    elif timeFormat.endswith("ps"):
        time_format += "-12, " + precision + ", \" ps\", 0);"
    elif timeFormat.endswith("ns"):
        time_format += "-9, " + precision + ", \" ns\", 0);"
    elif timeFormat.endswith("us"):
        time_format += "-6, " + precision + ", \" us\", 0);"
    elif timeFormat.endswith("ms"):
        time_format += "-3, " + precision + ", \" ms\", 0);"
    elif timeFormat.endswith("s"):
        time_format += "0, " + precision + ", \" s\", 0);"
    else:
        printError(1, "Unknown time format: " + yamlData['Time_Format'])
        exit(1)
    templateTB_sv_str = templateTB_sv_str.replace("#TIME_FORMAT#", time_format)

#------------------------------------------------------------------------------#
    # Insert the ports into the exerciser declaration

    exerciserPorts = ""
    with open(templateTB_sv,'r') as f:
        l = [line for line in f if "#EXERCISER_PORTS#" in line]
    leading_spaces = getIndentation(l)
    for clock in clocks_in:
        if exerciserPorts != "":
            exerciserPorts += leading_spaces
        exerciserPorts += "output logic " + clock['name'] + ",\n"
    for interface in interface_in:
        currInterface = usedInterfaces[interface['type']]
        for channel in interface['channels']:
            exerciserPorts += leading_spaces
            if channel['type'] in currInterface.master_input_channels:
                exerciserPorts += "input "
            else:
                exerciserPorts += "output "
            exerciserPorts += "logic " 
            if int(channel['size']) != 1:
                exerciserPorts += "[" + str(int(channel['size'])-1) + ":0] "
            exerciserPorts += interface['name'] + "_" + channel['type'] + ",\n"

    for interface in interface_out:
        currInterface = usedInterfaces[interface['type']]
        for channel in interface['channels']:
            exerciserPorts += leading_spaces
            if channel['type'] in currInterface.master_output_channels:
                exerciserPorts += "input "
            else:
                exerciserPorts += "output "
            exerciserPorts += "logic " 
            if int(channel['size']) != 1:
                exerciserPorts += "[" + str(int(channel['size'])-1) + ":0] "
            exerciserPorts += interface['name'] + "_" + channel['type'] + ",\n"
    for signal in signals_in:
        exerciserPorts += leading_spaces + "output logic " 
        if int(signal['size']) != 1:
            exerciserPorts += "[" + str(int(signal['size'])-1) + ":0] "
        exerciserPorts += signal['name'] + ",\n"
    for signal in signals_out:
        exerciserPorts += leading_spaces + "input logic " 
        if int(signal['size']) != 1:
            exerciserPorts += "[" + str(int(signal['size'])-1) + ":0] "
        exerciserPorts += signal['name'] + ",\n"
    templateTB_sv_str = templateTB_sv_str.replace("#EXERCISER_PORTS#", 
        exerciserPorts[:-2])

#------------------------------------------------------------------------------#
    # Instantiate the DUT

    dut_inst = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#DUT_INST#" in line]
    leading_spaces = getIndentation(lineStr)
    dut_inst += yamlData['Module_Name'] + " " + yamlData['Module_Name'] + "_i(\n"
    for clock in clocks_in:
        dut_inst += leading_spaces + tabSize + "." + clock['name'] + "(" + \
            clock['name'] + "),\n"
    for signal in signals_in:
        dut_inst += leading_spaces + tabSize + "." + signal['name'] + "(" + \
            signal['name'] + "),\n"
    for signal in signals_out:
        dut_inst += leading_spaces + tabSize + "." + signal['name'] + "(" + \
            signal['name'] + "),\n"
    for interface in interface_in:
        for channel in interface['channels']:
            dut_inst += leading_spaces + tabSize + "." + interface['name'] + \
                "_" + channel['name'] + "(" + interface['name'] + "_" + \
                channel['name'] + "),\n"
    for interface in interface_out:
        for channel in interface['channels']:
            dut_inst += leading_spaces + tabSize + "." + interface['name'] + \
            "_" + channel['name'] + "(" + interface['name'] + "_" + \
            channel['name'] + "),\n"
    dut_inst = dut_inst[:-2] + "\n"
    dut_inst += leading_spaces + ");"
    templateTB_sv_str = templateTB_sv_str.replace("#DUT_INST#", dut_inst)

#------------------------------------------------------------------------------#
    # Instantiate the exerciser

    exerciser_int = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#EXERCISER_INT#" in line]
    leading_spaces = getIndentation(lineStr)
    exerciser_int += "exerciser exerciser_i(\n"
    for index, clock in enumerate(clocks_in):
        exerciser_int += leading_spaces + tabSize + "." + clock['name'] + "(" + \
            clock['name'] + "),\n"
    for interface in interface_in:
        for channel in interface['channels']:
            exerciser_int += leading_spaces + tabSize + "." + interface['name'] \
                + "_" + channel['type'] + "(" + interface['name'] + "_" + \
                channel['name'] + "),\n"
    for interface in interface_out:
        for channel in interface['channels']:
            exerciser_int += leading_spaces + tabSize + "." + interface['name'] \
                + "_" + channel['type'] + "(" + interface['name'] + "_" + \
                channel['name'] + "),\n"
    for signal in signals_in:
        exerciser_int += leading_spaces + tabSize + "." + signal['name'] + "(" + \
            signal['name'] + "),\n"
    for signal in signals_out:
        exerciser_int += leading_spaces + tabSize + "." + signal['name'] + "(" + \
            signal['name'] + "),\n"
    exerciser_int = exerciser_int[:-2] + "\n"
    exerciser_int += leading_spaces + ");\n"
    templateTB_sv_str = templateTB_sv_str.replace("#EXERCISER_INT#", 
        exerciser_int[:-1])

#------------------------------------------------------------------------------#
    # Declare all the signals connecting the exerciser and the DUT

    tb_signal_list = ""
    maxSignalSize = 0
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#TB_SIGNAL_LIST#" in line]
    leading_spaces = getIndentation(lineStr)
    for clock in clocks_in:
        if tb_signal_list != "":
            tb_signal_list += leading_spaces
        tb_signal_list += "logic " + clock['name'] + ";\n"
    for signal in signals_in:
        if int(signal['size']) == 1:
           tb_signal_list += leading_spaces+ "logic " + signal['name'] + ";\n"
        else:
            tb_signal_list += leading_spaces+ "logic [" + str(int(signal['size']) \
                - 1) + ":0] " + signal['name'] + ";\n"
        if int(signal['size']) > maxSignalSize:
            maxSignalSize = int(signal['size'])
    for signal in signals_out:
        if int(signal['size']) == 1:
           tb_signal_list += leading_spaces+ "logic " + signal['name'] + ";\n"
        else:
            tb_signal_list += leading_spaces + "logic [" + str(int(signal['size']) \
                - 1) + ":0] " + signal['name'] + ";\n"
        if int(signal['size']) > maxSignalSize:
            maxSignalSize = int(signal['size'])
    for interface in interface_in:
        for channel in interface['channels']:
            if int(channel['size']) == 1:
                tb_signal_list += leading_spaces+ "logic " + interface['name'] + \
                    "_" + channel['name'] + ";\n"
            else:
                tb_signal_list += leading_spaces + "logic [" + \
                    str(int(channel['size']) - 1) + ":0] " + interface['name'] + \
                    "_" + channel['name'] + ";\n"
            if int(channel['size']) > maxSignalSize:
                maxSignalSize = int(channel['size'])
    for interface in interface_out:
        for channel in interface['channels']:
            if int(channel['size']) == 1:
                tb_signal_list += leading_spaces+ "logic " + interface['name'] + \
                    "_" + channel['name'] + ";\n"
            else:
                tb_signal_list += leading_spaces + "logic [" + \
                    str(int(channel['size']) - 1) + ":0] " + interface['name'] + \
                    "_" + channel['name'] + ";\n"
            if int(channel['size']) > maxSignalSize:
                maxSignalSize = int(channel['size'])
    templateTB_sv_str = templateTB_sv_str.replace("#TB_SIGNAL_LIST#", \
        tb_signal_list[:-1])
    templateTB_sv_str = templateTB_sv_str.replace("#MAX_DATA_SIZE#", \
        str(maxSignalSize))
    templateTB_c_str = templateTB_c_str.replace("#MAX_DATA_SIZE#", \
        str(maxSignalSize))

#------------------------------------------------------------------------------#
    # Create the if-else tree to set individual signals

    ifelse_signal = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#IF_ELSE_SIGNAL#" in line]
    leading_spaces = getIndentation(lineStr)
    for signal in signals_in:
        if ifelse_signal == "":
            ifelse_signal += "if(interfaceType_par == \"" + signal['name'] + \
                "\") begin\n" + leading_spaces + tabSize + signal['name'] + \
                " = args[0];\n" + leading_spaces + "end\n"
        else:
            ifelse_signal += leading_spaces + "else if(interfaceType_par == \"" \
                + signal['name'] + "\") begin\n" + leading_spaces + tabSize + \
                signal['name'] + " = args[0];\n" + leading_spaces + "end\n"
    for interface in interface_in:
        currInterface = usedInterfaces[interface['type']]
        for channel in interface['channels']:
            if channel['type'] in currInterface.master_output_channels:
                if ifelse_signal == "":
                    ifelse_signal += "if(interfaceType_par == \""
                else:
                    ifelse_signal += leading_spaces + "else if(interfaceType_par == \""
                ifelse_signal += interface['name'] + "_" + channel['name'] + \
                    "\") begin\n" + leading_spaces + tabSize + interface['name'] + \
                    "_" + channel['type'] + " = args[0];\n" + leading_spaces + "end\n"
    for interface in interface_out:
        interfaceType = interface['type']
        for channel in interface['channels']:
            if channel['type'] in currInterface.master_input_channels:
                if ifelse_signal == "":
                    ifelse_signal += "if(interfaceType_par == \""
                else:
                    ifelse_signal += leading_spaces + "else if(interfaceType_par == \""
                ifelse_signal += interface['name'] + "_" + channel['name'] + \
                    "\") begin\n" + leading_spaces + tabSize + interface['name'] + \
                    "_" + channel['type'] + " = args[0];\n" + leading_spaces + "end\n"
    templateTB_sv_str = templateTB_sv_str.replace("#IF_ELSE_SIGNAL#", ifelse_signal[:-1])

#------------------------------------------------------------------------------#
    # Create the if-else tree for interfaces

    elseif_interfaceIn = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#ELSE_IF_INTERFACE_IN#" in line]
    leading_spaces = getIndentation(lineStr)
    for interface in interface_in:
        currInterface = usedInterfaces[interface['type']]
        if elseif_interfaceIn != "":
            elseif_interfaceIn += leading_spaces
        elseif_interfaceIn += "else if(interfaceType_par == \"" + \
            interface['name'] + "\") begin\n"
        elseif_interfaceIn = commandVarReplace(elseif_interfaceIn, interface, 
            currInterface.slave_action, leading_spaces + tabSize, currInterface.sv_args)
    elseif_interfaceIn += leading_spaces + "end\n"
    templateTB_sv_str = templateTB_sv_str.replace("#ELSE_IF_INTERFACE_IN#", 
        elseif_interfaceIn[:-1])

    elseif_interfaceOut = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#ELSE_IF_INTERFACE_OUT#" in line]
    leading_spaces = getIndentation(lineStr)
    for interface in interface_out:
        currInterface = usedInterfaces[interface['type']]
        if elseif_interfaceOut != "":
            elseif_interfaceOut += leading_spaces
        elseif_interfaceOut += "else if(interfaceType_par == \"" + \
            interface['name'] + "\") begin\n"
        elseif_interfaceOut = commandVarReplace(elseif_interfaceOut, interface, 
            currInterface.master_action, leading_spaces + tabSize, currInterface.sv_args)
    elseif_interfaceOut += leading_spaces + "end\n"
    templateTB_sv_str = templateTB_sv_str.replace("#ELSE_IF_INTERFACE_OUT#", 
        elseif_interfaceOut[:-1])

    elseif_interfaceIn = ""
    with open(templateTB_c,'r') as f:
        lineStr = [line for line in f if "#ELSE_IF_INTERFACE_IN#" in line]
    leading_spaces = getIndentation(lineStr)
    for interface in interface_in:
        currInterface = usedInterfaces[interface['type']]
        if elseif_interfaceIn != "":
            elseif_interfaceIn += leading_spaces + "else "
        elseif_interfaceIn += "if(!strcmp(interfaceType,\"" + interface['name'] + \
            "\")){\n"
        elseif_interfaceIn += leading_spaces + tabSize + "WRITE(" + \
            interface['name'] + ")\n"
        elseif_interfaceIn += leading_spaces + "}\n"
    templateTB_c_str = templateTB_c_str.replace("#ELSE_IF_INTERFACE_IN#", 
        elseif_interfaceIn[:-1])

    elseif_interfaceOut = ""
    with open(templateTB_c,'r') as f:
        lineStr = [line for line in f if "#ELSE_IF_INTERFACE_OUT#" in line]
    leading_spaces = getIndentation(lineStr)
    for interface in interface_out:
        currInterface = usedInterfaces[interface['type']]
        if elseif_interfaceOut != "":
            elseif_interfaceOut += leading_spaces + "else "
        if elseif_interfaceIn != "" and elseif_interfaceOut == "":
            elseif_interfaceOut += "else "
        elseif_interfaceOut += "if(!strcmp(interfaceType,\"" + interface['name'] + \
            "\")){\n"
        elseif_interfaceOut += leading_spaces + tabSize + "read = true;\n"
        elseif_interfaceOut += leading_spaces + tabSize + "READ(" + \
            interface['name'] + ")\n"
        elseif_interfaceOut += leading_spaces + "}\n"
    templateTB_c_str = templateTB_c_str.replace("#ELSE_IF_INTERFACE_OUT#", 
        elseif_interfaceOut[:-1])

#------------------------------------------------------------------------------#
    # Create all testbench-generated clocks. Use the clock with the largest 
    # period between test vectors (not sure if necessary to use the largest)

    initial_clock = ""
    largestClock = ""
    largestPeriod = 0
    regex_int_str = re.compile("([0-9]+)([a-z]+)")
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#INITIAL_CLOCK#" in line]
    leading_spaces = getIndentation(lineStr)
    for clock in clocks_in:
        if initial_clock != "":
            initial_clock += leading_spaces
        initial_clock += "initial begin\n"
        initial_clock += leading_spaces + tabSize + clock['name'] + " = 0;\n"
        initial_clock += leading_spaces + tabSize + "forever begin\n"
        initial_clock += leading_spaces + tabSize + tabSize + "#(" + \
            clock['period'] + "/2) " + clock['name'] + " <= ~" + clock['name'] + \
            ";\n"
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

#------------------------------------------------------------------------------#
    # Create the if-else tree for waits

    if_else_wait = ""
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#IF_ELSE_WAIT#" in line]
    leading_spaces = getIndentation(lineStr)
    for condition in waitConditions:
        if if_else_wait != "":
            if_else_wait += leading_spaces + "else "
        if_else_wait += "if(interfaceType_par == \"" + condition['key'] + "\") begin\n"
        conditionStr = condition['condition'].replace("$value", "args[0]")
        if not conditionStr.endswith(";"):
            conditionStr += ";"
        if_else_wait += leading_spaces + tabSize + conditionStr + "\n"
        if_else_wait += leading_spaces + "end\n"
    templateTB_sv_str = templateTB_sv_str.replace("#IF_ELSE_WAIT#", if_else_wait[:-1])

#------------------------------------------------------------------------------#
    # This was meant to handle the use of interfaces in the testbench. For now,
    # this code is left for future work.

    # tb_axis_list = ""
    # with open(templateTB_sv,'r') as f:
    #     lineStr = [line for line in f if "#TB_AXIS_LIST#" in line]
    # leading_spaces = getIndentation(lineStr)
    # for interface in interface_in:
    #     currInterface = usedInterfaces[interface['type']]
    #     interfaceFilePath = getFilePath("env", "SONAR_PATH", "/include/" + \
    #         interface['type'] + ".sv")
    #     with open(interfaceFilePath) as f:
    #         interfaceFileStr = f.read()
    #     if tb_axis_list != "":
    #         tb_axis_list += leading_spaces
    #     interfaceName = currInterface.interface['name']
    #     tb_axis_list += interfaceName
    #     if currInterface.interface['parameters']:
    #         tb_axis_list += " #(\n"
    #         regex_interface_def = re.compile("interface " + interfaceName + \
    #             "(.|\n)+?(?=;)")
    #         regex_parameter_def = re.compile("parameter (.|\n)+?(?=(,|\)))")
    #         interface_def = regex_interface_def.match(interfaceFileStr)
    #         print(interface_def.group(1))
    #         for parameter in re.findall(regex_parameter_def, interface_def.group(1)):
    #             print(parameter)
    #     else:
    #         tb_axis_list += ""

    # for axis_in in axis_interfaces_in:
    #     if tb_axis_list != "":
    #         tb_axis_list += leading_spaces
    #     for interface in axis_in['interface']:
    #         if interface['type'] == "tdata":
    #             tdataSize = interface['size']
    #     tb_axis_list += "axi_stream " + axis_in['name'] + "(\n"
    #     tb_axis_list += leading_spaces + tabSize + ".aclk(" + axis_in['clock'] + \
    #         ")\n"
    #     tb_axis_list += leading_spaces + ");\n"
    #     tb_axis_list += leading_spaces + "axis_m #(\n" 
    #     tb_axis_list += leading_spaces + tabSize + ".DATA_WIDTH(" + \
    #         str(tdataSize) + ")\n" 
    #     tb_axis_list += leading_spaces + ") " + axis_in['name'] + "_m(\n"
    #     tb_axis_list += leading_spaces + tabSize + ".AXIS_M(" + axis_in['name'] + \
    #         "),\n"
    #     for interface in axis_in['interface']:
    #         tb_axis_list += leading_spaces + tabSize + "." + interface['type'] + \
    #             "(" + axis_in['name'] + "_" + interface['name'] + "),\n"
    #     tb_axis_list = tb_axis_list[:-2] + "\n"
    #     tb_axis_list += leading_spaces + ");\n"
    # for axis_out in axis_interfaces_out:
    #     if tb_axis_list != "":
    #         tb_axis_list += leading_spaces
    #     for interface in axis_out['interface']:
    #         if interface['type'] == "tdata":
    #             tdataSize = interface['size']
    #     tb_axis_list += "axi_stream " + axis_out['name'] + "(\n"
    #     tb_axis_list += leading_spaces + tabSize + ".aclk(" + axis_out['clock'] + \
    #         ")\n"
    #     tb_axis_list += leading_spaces + ");\n"
    #     tb_axis_list += leading_spaces + "axis_s #(\n" 
    #     tb_axis_list += leading_spaces + tabSize + ".DATA_WIDTH(" + \
    #         str(tdataSize) + ")\n" 
    #     tb_axis_list += leading_spaces + ") " + axis_out['name'] + "_s(\n"
    #     tb_axis_list += leading_spaces + tabSize + ".AXIS_S(" + axis_out['name'] + \
    #         "),\n"
    #     for interface in axis_out['interface']:
    #         tb_axis_list += leading_spaces + tabSize + "." + interface['type'] + \
    #             "(" + axis_out['name'] + "_" + interface['name'] + "),\n"
    #     tb_axis_list = tb_axis_list[:-2] + "\n"
    #     tb_axis_list += leading_spaces + ");\n"
    # templateTB_sv_str = templateTB_sv_str.replace("#TB_AXIS_LIST#", tb_axis_list[:-1])

    # axis_assign = ""
    # with open(templateTB_sv,'r') as f:
    #     lineStr = [line for line in f if "#AXIS_ASSIGN#" in line]
    # leading_spaces = getIndentation(lineStr)
    # for axis_in in axis_interfaces_in:
    #     if axis_assign != "":
    #         axis_assign += leading_spaces
    #     axis_assign += axis_in['name'] + "_m.write();\n"
    # for axis_out in axis_interfaces_out:
    #     if axis_assign != "":
    #         axis_assign += leading_spaces
    #     axis_assign += axis_out['name'] + "_s.read();\n"
    # templateTB_sv_str = templateTB_sv_str.replace("#AXIS_ASSIGN#", axis_assign[:-1])

#------------------------------------------------------------------------------#
    # Create a JSON file (for legacy reasons) for the next script to work with.
    # i.e. expand all the YAML macros, fill in missing interface signal keys etc

    parallelNum = writeJSON(yamlData['Test_Vectors'], dataFile, signals_in, 
    signals_out, interface_in, interface_out, usedInterfaces)
                     
    templateTB_sv_str = templateTB_sv_str.replace("#MAX_PARALLEL#", str(parallelNum))

    dataFile.close()
    configFile.close()
    # tbFile_sv.close()

    generate("absolute", None, dataFileName) #parse the JSON and continue

    with open(tbFileName_sv.replace("tb.sv", "sv.dat")) as f:
        line = f.readline()
        maxArgs = 0
        while line:
            firstWord = line.split(' ')[0]
            if firstWord not in ['TestVector', 'ParallelSection', 'Packet']:
                argCount = int(quoteSplit(line)[2])
                if argCount > maxArgs:
                    maxArgs = argCount
            line = f.readline()

    with open(tbFileName_c.replace("tb.cpp", "c.dat")) as f:
        line = f.readline()
        maxCharLength = 0
        while line:
            firstWord = line.split(' ')[0]
            secondWord = line.split(' ')[1]
            if len(firstWord) > maxCharLength:
                maxCharLength = len(firstWord)
            if len(secondWord) > maxCharLength:
                maxCharLength = len(secondWord)
            line = f.readline()
    
    with open(templateTB_sv,'r') as f:
        lineStr = [line for line in f if "#MAX_ARG_NUM#" in line]
    leading_spaces = getIndentation(lineStr)
    templateTB_sv_str = templateTB_sv_str.replace("#MAX_ARG_NUM#", str(maxArgs))
    templateTB_c_str = templateTB_c_str.replace("#MAX_ARG_NUM#", str(maxArgs))

    with open(templateTB_c,'r') as f:
        lineStr = [line for line in f if "#MAX_ARG_NUM#" in line]
    leading_spaces = getIndentation(lineStr)
    templateTB_c_str = templateTB_c_str.replace("#MAX_STRING_SIZE#", str(maxCharLength))

    tbFile_sv.write(templateTB_sv_str)
    tbFile_sv.close()

    tbFile_c.write(templateTB_c_str)
    tbFile_c.close()

################################################################################

if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "-h" or arg == "--help":
            print("Usage: python sonar.py mode modeArg filename")
            print("  mode: env - use relative path from an environment variable")
            print("        path - use relative path from a string")
            print("        absolute - use absolute filepath")
            print("  modeArg: environment variable or path string. None otherwise")
            print("  filename: user file to read")

    if (len(sys.argv) == 4):
        sonar(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Incorrect number of arguments. Use -h or --help")