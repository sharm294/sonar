import copy
import datetime
import json
import logging
import os
import re
import sys
from shlex import split as quoteSplit

# from .generate import generate
# from .include.utilities import (getFilePath, getIndentation, getInterface,
#                                 printError, stripFileName)
# from .writeJSON import writeJSON
from sonar.exceptions import SonarInvalidArgError
from sonar.core.backends.sv import create_testbench as create_sv_testbench
from sonar.core.backends.cpp import create_testbench as create_cpp_testbench

logger = logging.getLogger(__name__)

TAB_SIZE = "    "

################################################################################
### _byteify ###
# This function returns the string object when reading JSON instead of
# Unicode coded strings which cause key errors when parsing. This is taken from
# stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json


def json_load_byteified(file_handle):
    # return _byteify(json.load(file_handle, object_hook=_byteify), ignore_dicts=True)
    return json.load(file_handle)


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode("utf-8")
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.items()
        }
    # if it's anything else, return it in its original form
    return data


################################################################################
### channelToIndex ###
# This function finds the index of a particular channel based on its name
def channelToIndex(channelType, args):
    for idx, channel in enumerate(args):
        if channel == channelType:
            return idx

    printError(1, "Unknown channel: " + channelType)
    return None


################################################################################
### replaceVar ###
# This function relaces all $$X variables using the interface as the source
def replaceVar(inputStr, interface, key=None):
    regex_variable = re.compile(r"\$\$[^_|\W]+")
    for variable in re.findall(regex_variable, inputStr):
        new_variable = interface[variable[2:]]
        if isinstance(new_variable, (list, dict, tuple)):
            new_variable = new_variable[key]
        inputStr = inputStr.replace(variable, str(new_variable))
    return inputStr


################################################################################
### commandVarReplaceSub ###
# This function replaces any $variables with their corresponding key from the
# YAML
def commandVarReplaceSub(elseif_interfaceIn, command, interface, indent, key=None):
    command = command.replace("$$name", interface["name"])
    command = replaceVar(command, interface, key)
    # regex_variable = re.compile("\$\$[^_|\W]+")
    # for variable in re.findall(regex_variable, command):
    #     command = command.replace(variable, interface[variable[2:]])
    command = command.replace("\n", "\n" + indent)
    elseif_interfaceIn += indent + command + "\n"
    return elseif_interfaceIn


################################################################################
### commandVarReplaceChannel ###
# This function performs duplication and text replacement for $$channels
def commandVarReplaceChannel(
    interface, action, command, elseif_interfaceIn, indent, args
):
    for channel in interface["channels"]:
        if channel["type"] in action["channels"]:
            commandCopy = copy.deepcopy(command)
            commandCopy = commandCopy.replace("$$channel", channel["type"])
            idx = str(channelToIndex(channel["type"], args))
            commandCopy = commandCopy.replace("$$i", idx)
            elseif_interfaceIn = commandVarReplaceSub(
                elseif_interfaceIn, commandCopy, interface, indent
            )
    return elseif_interfaceIn


# This function replaces the variables in an interface action block. There are
# two named variables: $$name (referring to the interface name) and $$channel (
# referring to a particular side channel). All other $$ variables must be keys in
# the interface declaration in the configuration file
def commandVarReplace(elseif_interfaceIn, interface, actions, indent, args):
    for action in actions:
        # check if there is a command to repeat for a set of channels
        if isinstance(action, dict):
            if "channels" in action:
                for command in action["commands"]:
                    regex_channel = re.compile(r"\$\$channel")
                    if re.findall(regex_channel, command):  # if $$channel in command
                        elseif_interfaceIn = commandVarReplaceChannel(
                            interface, action, command, elseif_interfaceIn, indent, args
                        )
                    else:
                        commandCopy = copy.deepcopy(command)
                        elseif_interfaceIn = commandVarReplaceSub(
                            elseif_interfaceIn, commandCopy, interface, indent
                        )
            else:
                for index, entity in enumerate(interface[action["foreach"]]):
                    for command in action["commands"]:
                        commandCopy = copy.deepcopy(command)
                        elseif_interfaceIn = commandVarReplaceSub(
                            elseif_interfaceIn, commandCopy, interface, indent, index
                        )
        else:
            commandCopy = copy.deepcopy(action)
            elseif_interfaceIn = commandVarReplaceSub(
                elseif_interfaceIn, commandCopy, interface, indent
            )

    return elseif_interfaceIn


def replace_in_testbenches(testbenches, search_str, replace, include_langs=None, exclude_langs=None):
    for lang in [*testbenches]:
        if include_langs:
            if lang not in include_langs:
                continue
        if exclude_langs:
            if lang in exclude_langs:
                continue
        
        if isinstance(replace, dict):
            if lang in replace:
                replace_str = str(replace[lang]).replace("$$lang", lang)
            else:
                replace_str = ""
        else:
            replace_str = str(replace).replace("$$lang", lang)
        testbenches[lang] = testbenches[lang].replace(search_str, replace_str)

def set_metadata(testbench, testbenches):
    """
    Perform the direct substitutions from the sonar testbench metadata into the
    the testbench

    Args:
        testbench (Testbench): Sonar testbench description
        testbenches (dict): The testbench templates indexed by language

    Returns:
        dict: Updated testbench templates
    """
    for key, value in testbench["metadata"].items():
        if value is None:
            replace_str = ""
        else:
            replace_str = str(value)
        search_str = "SONAR_" + key.upper()
        replace_in_testbenches(testbenches, search_str, replace_str)

    return testbenches


def modify_signal_names():
    pass

def hoopla(testbench, testbenches, directory):    
    # set the directly replaceable text into the testbench
    testbenches = set_metadata(testbench, testbenches)

    replace_in_testbenches(testbenches, "SONAR_CURR_DATE", datetime.datetime.now())
    replace_in_testbenches(testbenches, "SONAR_DATA_FILE", f'"{testbench["metadata"]["Module_Name"]}_$$lang.dat')
    replace_in_testbenches(testbenches, "SONAR_FUNCTION", f'"{testbench["metadata"]["Module_Name"].upper()}')
    replace_in_testbenches(testbenches, "SONAR_MAX_VECTORS", len(testbench["vectors"]))

    if "Headers" in testbench["metadata"]:
        sv_headers = ""
        c_headers = ""
        headers = {
            "cpp": "",
            "sv": ""
        }
        for header_tuple in testbench["metadata"]["Headers"]:
            if isinstance(header_tuple, (list, tuple)):
                header_file = header_tuple[0]
                header_mode = header_tuple[1]
            else:
                header_file = header_tuple
                header_mode = "auto"
            if header_mode == "cpp":
                headers["cpp"] += f'#include "{header_file}"\n'
            elif header_mode == "sv":
                headers["sv"] += f'`include "{header_file}"\n'
            else:
                if header_file.endswith((".h", ".hpp")):
                    headers["cpp"] += f'#include "{header_file}"\n'
                elif header_file.endswith((".v", ".sv")):
                    headers["sv"] += f'`include "{header_file}"\n'
                else:
                    print(f"Skipped adding unknown header file type: {header_file}")
        replace_in_testbenches(testbenches, "SONAR_HEADER_FILE", headers)

    # ------------------------------------------------------------------------------#
    # Read configuration file into separate structures for easier access

    # Direction is relative to the DUT
    resets_in = testbench["modules"]["DUT"]["resets_in"]
    clocks_in = testbench["modules"]["DUT"]["clocks_in"]
    signals_in = testbench["modules"]["DUT"]["signals_in"]
    signals_out = testbench["modules"]["DUT"]["signals_out"]
    interfaces = {
        "slave": testbench["modules"]["DUT"]["interfaces_slave"],
        "master": testbench["modules"]["DUT"]["interfaces_master"],
        "mixed": testbench["modules"]["DUT"]["interfaces_mixed"]
    }
    parameters = testbench["modules"]["DUT"]["parameters"]

    interface_indices = {}
    used_interfaces = {}

    for direction in ["slave", "master", "mixed"]:
        for index, interface in enumerate(interfaces[direction]):
            try:
                used_interfaces[interface["type"]] = getInterface(interface["type"])
            except ImportError as ex:
                logger.error("Interface %s not found in sonar", interface["type"])
                raise SonarInvalidArgError from ex
            if interface["type"] not in interface_indices:
                interface_indices[interface["type"]] = 0
            else:
                interface_indices[interface["type"]] += 1
            # portCopy = interface.copy()
            # for channel in portCopy["channels"]:
            #     if "size" not in channel:
            #         channel["size"] = 1
            # if "connection_mode" not in portCopy:
            #     portCopy["connection_mode"] = "native"
            interfaces[direction][index]["index"] = interface_indices[interface["type"]]
            if hasattr(used_interfaces[interface["type"]], "yaml_top"):
                interfaces[direction][index]["index"] = used_interfaces[interface["type"]].yaml_top(interface)

    wait_conditions = testbench["wait_conditions"]

    time_format_str = "$timeformat("
    precision = str(testbench["metadata"]["Time_Format"]["precision"])
    time_format = testbench["metadata"]["Time_Format"]["unit"]
    if time_format.endswith("fs"):
        time_format_str += "-15, " + precision + ', " fs", 0);'
    elif time_format.endswith("ps"):
        time_format_str += "-12, " + precision + ', " ps", 0);'
    elif time_format.endswith("ns"):
        time_format_str += "-9, " + precision + ', " ns", 0);'
    elif time_format.endswith("us"):
        time_format_str += "-6, " + precision + ', " us", 0);'
    elif time_format.endswith("ms"):
        time_format_str += "-3, " + precision + ', " ms", 0);'
    elif time_format.endswith("s"):
        time_format_str += "0, " + precision + ', " s", 0);'
    else:
        logger.error("Unknown time format: %s", testbench["metadata"]["Time_Format"])
        raise SonarInvalidArgError
    replace_in_testbenches(testbenches, "SONAR_TIME_FORMAT", time_format_str, include_langs=["sv"])

    # ------------------------------------------------------------------------------#
    # Import any packages that interfaces may use
    imports = ""
    for name, interface in used_interfaces.items():
        if hasattr(interface, "import_packages_global"):
            imports += interface.import_packages_global()
    for direction in ["slave", "master", "mixed"]:
        for interface in interfaces[direction]:
            curr_interface = used_interfaces[interface["type"]]
            if hasattr(curr_interface, "import_packages_local"):
                imports += curr_interface.import_packages_local(interface)
    replace_in_testbenches(testbenches, "SONAR_IMPORT_PACKAGES", imports[:-1], include_langs=["sv"])

    # ------------------------------------------------------------------------------#
    # Add any statements an interface might require within an initial block
    initial_prologue = ""
    leading_spaces = getIndentation("SONAR_INITIAL_PROLOGUE", testbenches["sv"])
    for direction in ["slave", "master", "mixed"]:
        for interface in interfaces[direction]:
            curr_interface = used_interfaces[interface["type"]]
            if hasattr(curr_interface, "initial_prologue"):
                initial_prologue = curr_interface.initial_prologue(
                    initial_prologue, interface, leading_spaces
                )
                initial_prologue = replaceVar(initial_prologue, interface)
    replace_in_testbenches(testbenches, "SONAR_INITIAL_PROLOGUE", initial_prologue[:-1], include_langs=["sv"])

    # ------------------------------------------------------------------------------#
    # Add any statements an interface might require within outside an initial block
    exerciser_prologue = ""
    leading_spaces = getIndentation("SONAR_EXERCISER_PROLOGUE", testbenches["sv"])
    for direction in ["slave", "master", "mixed"]:
        for interface in interfaces[direction]:
            curr_interface = used_interfaces[interface["type"]]
            if hasattr(curr_interface, "exerciser_prologue"):
                exerciser_prologue = curr_interface.exerciser_prologue(
                    exerciser_prologue, interface, leading_spaces
                )
                exerciser_prologue = replaceVar(exerciser_prologue, interface)
    replace_in_testbenches(testbenches, "SONAR_EXERCISER_PROLOGUE", exerciser_prologue[:-1], include_langs=["sv"])

    # ------------------------------------------------------------------------------#
    # Run any TCL scripts in Vivado as required by interfaces
    for direction in ["slave", "master", "mixed"]:
        for interface in interfaces[direction]:
            curr_interface = used_interfaces[interface["type"]]
            if hasattr(curr_interface, "source_tcl"):
                curr_interface.source_tcl(interface, directory)
    # ------------------------------------------------------------------------------#
    # Insert the ports into the exerciser declaration

    exerciser_ports = ""
    leading_spaces = getIndentation("SONAR_EXERCISER_PORTS", testbenches["sv"])
    for clock in clocks_in:
        if exerciser_ports != "":
            exerciser_ports += leading_spaces
        exerciser_ports += "output logic " + clock["name"] + ",\n"
    for direction in ["slave", "master", "mixed"]:
        for interface in interfaces[direction]:
            curr_interface = used_interfaces[interface["type"]]
            for channel in interface["channels"]:
                exerciser_ports += leading_spaces
                if direction in ["slave", "mixed"]:
                    if channel["type"] in curr_interface.master_input_channels:
                        exerciser_ports += "input "
                    else:
                        exerciser_ports += "output "
                else:
                    if channel["type"] in curr_interface.master_output_channels:
                        exerciser_ports += "input "
                    else:
                        exerciser_ports += "output "
                exerciser_ports += "logic "
                if int(channel["size"]) != 1:
                    exerciser_ports += "[" + str(int(channel["size"]) - 1) + ":0] "
                exerciser_ports += interface["name"] + "_" + channel["type"] + ",\n"
    for signal in signals_in:
        exerciser_ports += leading_spaces + "output logic "
        if int(signal["size"]) != 1:
            exerciser_ports += "[" + str(int(signal["size"]) - 1) + ":0] "
        exerciser_ports += signal["name"] + ",\n"
    for signal in signals_out:
        exerciser_ports += leading_spaces + "input logic "
        if int(signal["size"]) != 1:
            exerciser_ports += "[" + str(int(signal["size"]) - 1) + ":0] "
        exerciser_ports += signal["name"] + ",\n"
    replace_in_testbenches(testbenches, "SONAR_EXERCISER_PORTS", exerciser_ports[:-2], include_langs=["sv"])

    instantiate_dut()

    # ------------------------------------------------------------------------------#
    # Instantiate the exerciser

    exerciser_int = ""
    leading_spaces = getIndentation("SONAR_EXERCISER_INT", testbenches["sv"])
    exerciser_int += "exerciser exerciser_i(\n"
    for index, clock in enumerate(clocks_in):
        exerciser_int += (
            leading_spaces
            + TAB_SIZE
            + "."
            + clock["name"]
            + "("
            + clock["name"]
            + "),\n"
        )
    for direction in ["slave", "master", "mixed"]:
        for interface in interfaces[direction]:
            if interface["connection_mode"] == "native":
                for channel in interface["channels"]:
                    exerciser_int += (
                        leading_spaces
                        + TAB_SIZE
                        + "."
                        + interface["name"]
                        + "_"
                        + channel["type"]
                        + "("
                        + interface["name"]
                        + "_"
                        + channel["type"]
                        + "),\n"
                    )
    for signal in (signals_in, signals_out):
        exerciser_int += (
            leading_spaces
            + TAB_SIZE
            + "."
            + signal["name"]
            + "("
            + signal["name"]
            + "),\n"
        )
    exerciser_int = exerciser_int[:-2] + "\n"
    exerciser_int += leading_spaces + ");\n"
    replace_in_testbenches(testbenches, "SONAR_EXERCISER_INT", exerciser_int[:-1], include_langs=["sv"])

    # ------------------------------------------------------------------------------#
    # Instantiate any IPs required by interfaces
    ip_inst = ""
    leading_spaces = getIndentation("SONAR_IP_INST", testbenches["sv"])
    for direction in ["slave", "master", "mixed"]:
        for interface in interfaces[direction]:
            curr_interface = used_interfaces[interface["type"]]
            if hasattr(curr_interface, "instantiate"):
                ip_inst = curr_interface.instantiate(
                    ip_inst, interface, leading_spaces, TAB_SIZE
                )
    replace_in_testbenches(testbenches, "SONAR_IP_INST", ip_inst[:-1], include_langs=["sv"])

    declare_signals()

    # ------------------------------------------------------------------------------#
    # Create the if-else tree to set individual signals in the exerciser

    set_signals()

    # ------------------------------------------------------------------------------#
    # Create the if-else tree for interfaces

    set_interfaces()

    # ------------------------------------------------------------------------------#
    # Create all testbench-generated clocks. Use the clock with the largest
    # period between test vectors (not sure if necessary to use the largest)
    
    create_clocks()

    # ------------------------------------------------------------------------------#
    # Create the if-else tree for waits
    
    set_waits()

    # ------------------------------------------------------------------------------#
    # This was meant to handle the use of interfaces in the testbench. For now,
    # this code is left for future work.

    # tb_axis_list = ""
    # with open(templateTB_sv,'r') as f:
    #     lineStr = [line for line in f if "SONAR_TB_AXIS_LIST" in line]
    # leading_spaces = getIndentation(lineStr)
    # for interface in interfaces_slave:
    #     curr_interface = used_interfaces[interface['type']]
    #     interfaceFilePath = getFilePath("env", "SONAR_PATH", "/include/" + \
    #         interface['type'] + ".sv")
    #     with open(interfaceFilePath) as f:
    #         interfaceFileStr = f.read()
    #     if tb_axis_list != "":
    #         tb_axis_list += leading_spaces
    #     interfaceName = curr_interface.interface['name']
    #     tb_axis_list += interfaceName
    #     if curr_interface.interface['parameters']:
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
    #     tb_axis_list += leading_spaces + TAB_SIZE + ".aclk(" + axis_in['clock'] + \
    #         ")\n"
    #     tb_axis_list += leading_spaces + ");\n"
    #     tb_axis_list += leading_spaces + "axis_m #(\n"
    #     tb_axis_list += leading_spaces + TAB_SIZE + ".DATA_WIDTH(" + \
    #         str(tdataSize) + ")\n"
    #     tb_axis_list += leading_spaces + ") " + axis_in['name'] + "_m(\n"
    #     tb_axis_list += leading_spaces + TAB_SIZE + ".AXIS_M(" + axis_in['name'] + \
    #         "),\n"
    #     for interface in axis_in['interface']:
    #         tb_axis_list += leading_spaces + TAB_SIZE + "." + interface['type'] + \
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
    #     tb_axis_list += leading_spaces + TAB_SIZE + ".aclk(" + axis_out['clock'] + \
    #         ")\n"
    #     tb_axis_list += leading_spaces + ");\n"
    #     tb_axis_list += leading_spaces + "axis_s #(\n"
    #     tb_axis_list += leading_spaces + TAB_SIZE + ".DATA_WIDTH(" + \
    #         str(tdataSize) + ")\n"
    #     tb_axis_list += leading_spaces + ") " + axis_out['name'] + "_s(\n"
    #     tb_axis_list += leading_spaces + TAB_SIZE + ".AXIS_S(" + axis_out['name'] + \
    #         "),\n"
    #     for interface in axis_out['interface']:
    #         tb_axis_list += leading_spaces + TAB_SIZE + "." + interface['type'] + \
    #             "(" + axis_out['name'] + "_" + interface['name'] + "),\n"
    #     tb_axis_list = tb_axis_list[:-2] + "\n"
    #     tb_axis_list += leading_spaces + ");\n"
    # templateTB_sv_str = templateTB_sv_str.replace("SONAR_TB_AXIS_LIST", tb_axis_list[:-1])

    # axis_assign = ""
    # with open(templateTB_sv,'r') as f:
    #     lineStr = [line for line in f if "SONAR_AXIS_ASSIGN" in line]
    # leading_spaces = getIndentation(lineStr)
    # for axis_in in axis_interfaces_in:
    #     if axis_assign != "":
    #         axis_assign += leading_spaces
    #     axis_assign += axis_in['name'] + "_m.write();\n"
    # for axis_out in axis_interfaces_out:
    #     if axis_assign != "":
    #         axis_assign += leading_spaces
    #     axis_assign += axis_out['name'] + "_s.read();\n"
    # templateTB_sv_str = templateTB_sv_str.replace("SONAR_AXIS_ASSIGN", axis_assign[:-1])

    # ------------------------------------------------------------------------------#
    # Create a JSON file (for legacy reasons) for the next script to work with.
    # i.e. expand all the YAML macros, fill in missing interface signal keys etc

    parallelNum = writeJSON(
        testbench["vectors"],
        dataFile,
        signals_in,
        signals_out,
        interfaces_slave,
        interfaces_master,
        used_interfaces,
    )

    templateTB_sv_str = templateTB_sv_str.replace(
        "SONAR_MAX_PARALLEL", str(parallelNum)
    )

    dataFile.close()
    configFile.close()
    # tbFile_sv.close()

    generate("absolute", None, dataFileName, languages)  # parse the JSON and continue

    with open(tb_filename_sv.replace("tb.sv", "sv.dat")) as f:
        line = f.readline()
        maxArgs = 0
        while line:
            firstWord = line.split(" ")[0]
            if firstWord not in ["TestVector", "ParallelSection", "Packet"]:
                argCount = int(quoteSplit(line)[2])
                if argCount > maxArgs:
                    maxArgs = argCount
            line = f.readline()

    if enable_C:
        with open(tb_filename_cpp.replace("tb.cpp", "c.dat")) as f:
            line = f.readline()
            maxCharLength = 0
            while line:
                firstWord = line.split(" ")[0]
                secondWord = line.split(" ")[1]
                thirdWord = line.split(" ")[2]
                if len(firstWord) > maxCharLength:
                    maxCharLength = len(firstWord)
                if len(secondWord) > maxCharLength:
                    maxCharLength = len(secondWord)
                if len(thirdWord) > maxCharLength:
                    maxCharLength = len(thirdWord)
                line = f.readline()

    with open(templateTB_sv, "r") as f:
        lineStr = [line for line in f if "SONAR_MAX_ARG_NUM" in line]
    leading_spaces = getIndentation(lineStr)
    templateTB_sv_str = templateTB_sv_str.replace("SONAR_MAX_ARG_NUM", str(maxArgs))

    if enable_C:
        templateTB_c_str = templateTB_c_str.replace("SONAR_MAX_ARG_NUM", str(maxArgs))
        with open(templateTB_c, "r") as f:
            lineStr = [line for line in f if "SONAR_MAX_ARG_NUM" in line]
        leading_spaces = getIndentation(lineStr)
        templateTB_c_str = templateTB_c_str.replace(
            "SONAR_MAX_STRING_SIZE", str(maxCharLength + 1)
        )  # /0 char


# TODO error handling
# TODO make seek size programmatic
# TODO add comments
# TODO clean up code and add functions
# TODO allow loops for commands (repeat)
# TODO allow delays by clock cycles
# TODO support floating clock periods
################################################################################
### sonar ###
# This function uses a configuration file to generate testbenches, data for the
# the testbenches to use, and a number of JSON files (for legacy reasons).
def sonar(testbench_config, sonar_tb_filepath, languages="sv"):
    if isinstance(languages, str):
        if languages == "all":
            active_langs = ("sv", "cpp")
        else:
            active_langs = (languages,)
    elif isinstance(languages, (list, tuple)):
        active_langs = tuple(languages)
    else:
        raise SonarInvalidArgError("Languages must be specified as a string or an iterable")
    
    dut_name = os.path.basename(sonar_tb_filepath)[:-3]
    directory = os.path.join(os.path.dirname(sonar_tb_filepath), "build", dut_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    def get_tb_filename(lang):
        return os.path.join(directory, dut_name + f"_tb.{lang}")

    def get_data_filename(lang):
        return os.path.join(directory, dut_name + f"_{lang}.dat")

    # if any of the generated testbenches are newer than the sonar testbench
    # script, skip generating it. This probably implies the user has manually
    # edited the generated testbench
    # sonar_tb_file_time = os.path.getmtime(sonar_tb_filepath)
    # active_langs_tmp = []
    # for lang in active_langs:
    #     if os.path.exists(get_tb_filename(lang)):
    #         tb_time = os.path.getmtime(get_tb_filename(lang))
    #         if tb_time <= sonar_tb_file_time:
    #             active_langs_tmp.append(lang)
    #     else:
    #         active_langs_tmp.append(lang)
    # active_langs = active_langs_tmp

    testbenches = {}
    data_files = {}
    for lang in active_langs:
        template = os.path.join(os.path.dirname(__file__), "templates", f"template_tb.{lang}")
        with open(template, "r") as f:
            testbenches[lang] = f.read()

    testbenches["sv"], data_files["sv"] = create_sv_testbench(testbench_config, testbenches["sv"], directory)
    testbenches["cpp"], data_files["cpp"] = create_cpp_testbench(testbench_config, testbenches["cpp"], directory)
    
    # testbenches = hoopla(testbench, testbenches, directory)

    for lang in active_langs:
        with open(get_tb_filename(lang), "w+") as f:
            f.write(testbenches[lang])
        with open(get_data_filename(lang), "w+") as f:
            f.write(data_files[lang])
