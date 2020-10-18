import datetime
import logging
import re
import itertools
import os

from shlex import split as quoteSplit

import sonar.core.backends.include as include
from sonar.exceptions import SonarInvalidArgError

TAB_SIZE = "    "

logger = logging.getLogger(__name__)

def add_headers(testbench_config, testbench):
    headers = ""
    if "Headers" in testbench_config.metadata:
        for header_tuple in testbench_config.metadata["Headers"]:
            if isinstance(header_tuple, (list, tuple)):
                header_file = header_tuple[0]
                header_mode = header_tuple[1]
            else:
                header_file = header_tuple
                header_mode = "auto"
            if header_mode == "sv":
                headers += f'`include "{header_file}"\n'
            elif header_mode == "auto":
                if header_file.endswith((".v", ".sv")):
                    headers += f'`include "{header_file}"\n'
    testbench = include.replace_in_testbenches(testbench, "SONAR_HEADER_FILE", headers)
    return testbench

def add_timeformat(testbench_config, testbench):
    time_format_str = "$timeformat("
    precision = str(testbench_config.metadata["Time_Format"]["precision"])
    time_format = testbench_config.metadata["Time_Format"]["unit"]
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
        logger.error("Unknown time format: %s", testbench_config.metadata["Time_Format"])
        raise SonarInvalidArgError
    testbench = include.replace_in_testbenches(testbench, "SONAR_TIMEFORMAT", time_format_str)
    return testbench

def add_imports(testbench_config, testbench, used_interfaces):
    # ------------------------------------------------------------------------------#
    # Import any packages that interfaces may use
    interfaces = include.get_from_dut(testbench_config, "interfaces")

    imports = ""
    for _name, interface in used_interfaces.items():
        if hasattr(interface, "import_packages_global"):
            imports += interface.import_packages_global()
    for interface in interfaces:
        curr_interface = used_interfaces[interface.type]
        if hasattr(curr_interface, "import_packages_local"):
            imports += curr_interface.import_packages_local(interface)
    testbench = include.replace_in_testbenches(testbench, "SONAR_IMPORT_PACKAGES", imports[:-1])
    return testbench

def add_initial_prologue(testbench_config, testbench, used_interfaces):
    # ------------------------------------------------------------------------------#
    # Add any statements an interface might require within an initial block
    interfaces = include.get_from_dut(testbench_config, "interfaces")

    initial_prologue = ""
    leading_spaces = include.get_indentation("SONAR_INITIAL_PROLOGUE", testbench)
    for interface in interfaces:
        curr_interface = used_interfaces[interface.type]
        if hasattr(curr_interface, "initial_prologue"):
            initial_prologue = curr_interface.initial_prologue(
                initial_prologue, interface, leading_spaces
            )
            initial_prologue = include.replaceVar(initial_prologue, interface)
    testbench = include.replace_in_testbenches(testbench, "SONAR_INITIAL_PROLOGUE", initial_prologue[:-1])
    return testbench

def add_exerciser_prologue(testbench_config, testbench, used_interfaces):
    # ------------------------------------------------------------------------------#
    # Add any statements an interface might require within outside an initial block
    interfaces = include.get_from_dut(testbench_config, "interfaces")

    exerciser_prologue = ""
    leading_spaces = include.get_indentation("SONAR_EXERCISER_PROLOGUE", testbench)
    for interface in interfaces:
        curr_interface = used_interfaces[interface.type]
        if hasattr(curr_interface, "exerciser_prologue"):
            exerciser_prologue = curr_interface.exerciser_prologue(
                exerciser_prologue, interface, leading_spaces
            )
            exerciser_prologue = include.replaceVar(exerciser_prologue, interface)
    testbench = include.replace_in_testbenches(testbench, "SONAR_EXERCISER_PROLOGUE", exerciser_prologue[:-1])
    return testbench

def add_tcl(testbench_config, used_interfaces, directory):
    # ------------------------------------------------------------------------------#
    # Run any TCL scripts in Vivado as required by interfaces
    interfaces = include.get_from_dut(testbench_config, "interfaces")

    for interface in interfaces:
        curr_interface = used_interfaces[interface.type]
        if hasattr(curr_interface, "source_tcl"):
            curr_interface.source_tcl(interface, directory)
    # return testbench

def add_exerciser_ports(testbench_config, testbench, used_interfaces):
    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")
    signals_in = dut.ports.get_signals("input")
    resets_in = dut.ports.get_resets("input")
    signals_out = dut.ports.get_signals("output")
    interfaces = include.get_from_dut(testbench_config, "interfaces_dict")
    
    init_signals = []

    exerciser_ports = ""
    leading_spaces = include.get_indentation("SONAR_EXERCISER_PORTS", testbench)
    for clock in clocks_in:
        if exerciser_ports != "":
            exerciser_ports += leading_spaces
        exerciser_ports += "output logic " + clock.name + ",\n"
    for direction in ["slave", "master", "mixed"]:
        for interface in interfaces[direction]:
            if interface.connection_mode != "native":
                continue
            curr_interface = used_interfaces[interface.type]
            for channel in interface.channels:
                exerciser_ports += leading_spaces
                if direction in ["slave", "mixed"]:
                    if channel["type"] in curr_interface.master_input_channels:
                        exerciser_ports += "input "
                    else:
                        exerciser_ports += "output "
                        init_signals.append(interface.name + "_" + channel["type"])
                else:
                    if channel["type"] in curr_interface.master_output_channels:
                        exerciser_ports += "input "
                    else:
                        exerciser_ports += "output "
                        init_signals.append(interface.name + "_" + channel["type"])
                exerciser_ports += "logic "
                if int(channel["size"]) != 1:
                    exerciser_ports += "[" + str(int(channel["size"]) - 1) + ":0] "
                exerciser_ports += interface.name + "_" + channel["type"] + ",\n"
    for signal in itertools.chain(signals_in, resets_in):
        exerciser_ports += leading_spaces + "output logic "
        if int(signal.size) != 1:
            exerciser_ports += "[" + str(int(signal.size) - 1) + ":0] "
        exerciser_ports += signal.name + ",\n"
        init_signals.append(signal.name)
    for signal in signals_out:
        exerciser_ports += leading_spaces + "input logic "
        if int(signal.size) != 1:
            exerciser_ports += "[" + str(int(signal.size) - 1) + ":0] "
        exerciser_ports += signal.name + ",\n"
    testbench = include.replace_in_testbenches(testbench, "SONAR_EXERCISER_PORTS", exerciser_ports[:-2])

    init_commands = []
    for init_signal in init_signals:
        init_commands.append({"signal": {"name": init_signal, "value": 0}})

    for i, vector in enumerate(testbench_config.vectors):
        for j, thread in enumerate(vector.threads):
            for k, command in enumerate(thread.commands):
                if "macro" in command and command["macro"] == "INIT_SIGNALS":
                    testbench_config.vectors[i].threads[j].commands[k]["commands"] = init_commands
                elif "interface" in command:
                    curr_interface = include.get_interface(command["interface"]["type"])
                    
                    new_packets = []
                    for packet in command["interface"]["payload"]:
                        new_packets.append(curr_interface.json_payload(packet))
                    testbench_config.vectors[i].threads[j].commands[k]["payload"] = new_packets

    return testbench, testbench_config

def instantiate_exerciser(testbench_config, testbench):
    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")
    signals = dut.ports.get_signals()
    resets = dut.ports.get_resets()
    interfaces = include.get_from_dut(testbench_config, "interfaces")

    exerciser_int = ""
    leading_spaces = include.get_indentation("SONAR_EXERCISER_INT", testbench)
    exerciser_int += "exerciser exerciser_i(\n"
    for clock in clocks_in:
        exerciser_int += (
            leading_spaces
            + TAB_SIZE
            + "."
            + clock.name
            + "("
            + clock.name
            + "),\n"
        )
    for interface in interfaces:
        if interface.connection_mode == "native":
            for channel in interface.channels:
                exerciser_int += (
                    leading_spaces
                    + TAB_SIZE
                    + "."
                    + interface.name
                    + "_"
                    + channel["type"]
                    + "("
                    + interface.name
                    + "_"
                    + channel["type"]
                    + "),\n"
                )
    for signal in itertools.chain(signals, resets):
        exerciser_int += (
            leading_spaces
            + TAB_SIZE
            + "."
            + signal.name
            + "("
            + signal.name
            + "),\n"
        )
    exerciser_int = exerciser_int[:-2] + "\n"
    exerciser_int += leading_spaces + ");\n"
    testbench = include.replace_in_testbenches(testbench, "SONAR_EXERCISER_INT", exerciser_int[:-1])
    return testbench

def instantiate_interface_ips(testbench_config, testbench, used_interfaces):
    # ------------------------------------------------------------------------------#
    # Instantiate any IPs required by interfaces
    interfaces = include.get_from_dut(testbench_config, "interfaces")

    ip_inst = ""
    leading_spaces = include.get_indentation("SONAR_IP_INST", testbench)
    for interface in interfaces:
        curr_interface = used_interfaces[interface.type]
        if hasattr(curr_interface, "instantiate"):
            ip_inst = curr_interface.instantiate(
                ip_inst, interface, leading_spaces, TAB_SIZE
            )
    testbench = include.replace_in_testbenches(testbench, "SONAR_IP_INST", ip_inst[:-1])
    return testbench

def instantiate_dut(testbench_config, testbench):
    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")
    signals_in = dut.ports.get_signals("input")
    resets_in = dut.ports.get_resets("input")
    signals_out = dut.ports.get_signals("output")
    parameters = include.get_from_dut(testbench_config, "parameters")
    interfaces = include.get_from_dut(testbench_config, "interfaces")

    dut_inst = ""
    leading_spaces = include.get_indentation("SONAR_DUT_INST", testbench)
    if parameters:
        dut_inst += testbench_config.metadata["Module_Name"] + " #(\n"
        for parameter in parameters[:-1]:
            dut_inst += (
                leading_spaces
                + TAB_SIZE
                + "."
                + parameter[0]
                + "("
                + str(parameter[1])
                + "),\n"
            )
        dut_inst += (
            leading_spaces
            + TAB_SIZE
            + "."
            + parameters[-1][0]
            + "("
            + str(parameters[-1][1])
            + ")\n"
        )
        dut_inst += (
            leading_spaces + ") " + testbench_config.metadata["Module_Name"] + "_i (\n"
        )
    else:
        dut_inst += (
            testbench_config.metadata["Module_Name"]
            + " "
            + testbench_config.metadata["Module_Name"]
            + "_i (\n"
        )
    for clock in clocks_in:
        dut_inst += (
            leading_spaces
            + TAB_SIZE
            + "."
            + clock.name
            + "("
            + clock.name
            + "),\n"
        )
    dut_type = testbench_config.modules["DUT"].type
    for signal in signals_in:
        port_name = signal.name
        if dut_type["lang"] != "sv":  # TODO temporary workaround
            if dut_type["hls"] == "vivado" and dut_type["hls_version"] == "2018.1":
                if "type" not in signal or signal["type"] != "reset":
                    port_name = port_name + "_V"
        dut_inst += (
            leading_spaces + TAB_SIZE + "." + port_name + "(" + signal.name + "),\n"
        )
    for reset in resets_in:
        port_name = reset.name
        dut_inst += (
            leading_spaces + TAB_SIZE + "." + port_name + "(" + reset.name + "),\n"
        )
    for signal in signals_out:
        if dut_type["lang"] != "sv":
            if dut_type["hls"] == "vivado" and dut_type["hls_version"] == "2018.1":
                port_name = signal.name + "_V"
        else:
            port_name = signal.name
        dut_inst += (
            leading_spaces + TAB_SIZE + "." + port_name + "(" + signal.name + "),\n"
        )
    for interface in interfaces:
        for channel in interface.channels:
            dut_inst += (
                leading_spaces
                + TAB_SIZE
                + "."
                + interface.name
                + "_"
                + channel["name"]
                + "("
                + interface.name
                + "_"
                + channel["type"]
                + "),\n"
            )
    dut_inst = dut_inst[:-2] + "\n"
    dut_inst += leading_spaces + ");"
    testbench = include.replace_in_testbenches(testbench, "SONAR_DUT_INST", dut_inst)

    return testbench

def declare_signals(testbench_config, testbench):
    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")
    signals = dut.ports.get_signals()
    resets = dut.ports.get_resets()
    interfaces = include.get_from_dut(testbench_config, "interfaces")

    tb_signal_list = ""
    max_signal_size = 0
    leading_spaces = include.get_indentation("SONAR_TB_SIGNAL_LIST", testbench)
    for clock in clocks_in:
        if tb_signal_list != "":
            tb_signal_list += leading_spaces
        tb_signal_list += "logic " + clock.name + ";\n"
    for signal in itertools.chain(signals, resets):
        if int(signal.size) == 1:
            tb_signal_list += leading_spaces + "logic " + signal.name + ";\n"
        else:
            tb_signal_list += (
                leading_spaces
                + "logic ["
                + str(int(signal.size) - 1)
                + ":0] "
                + signal.name
                + ";\n"
            )
        if int(signal.size) > max_signal_size:
            max_signal_size = int(signal.size)
    for interface in interfaces:
        for channel in interface.channels:
            if int(channel["size"]) == 1:
                tb_signal_list += (
                    leading_spaces
                    + "logic "
                    + interface.name
                    + "_"
                    + channel["type"]
                    + ";\n"
                )
            else:
                tb_signal_list += (
                    leading_spaces
                    + "logic ["
                    + str(int(channel["size"]) - 1)
                    + ":0] "
                    + interface.name
                    + "_"
                    + channel["type"]
                    + ";\n"
                )
            if int(channel["size"]) > max_signal_size:
                max_signal_size = int(channel["size"])
    testbench = include.replace_in_testbenches(testbench, "SONAR_TB_SIGNAL_LIST", tb_signal_list[:-1])
    testbench = include.replace_in_testbenches(testbench, "SONAR_MAX_DATA_SIZE", max_signal_size)
    return testbench

def set_signals(testbench_config, testbench, used_interfaces):
    dut = testbench_config.modules["DUT"]
    signals_in = dut.ports.get_signals("input")
    resets_in = dut.ports.get_resets("input")
    interfaces = include.get_from_dut(testbench_config, "interfaces")

    ifelse_signal = ""
    leading_spaces = include.get_indentation("SONAR_IF_ELSE_SIGNAL", testbench)
    for signal in itertools.chain(signals_in, resets_in):
        if ifelse_signal != "":
            ifelse_signal += leading_spaces + "else "
        ifelse_signal += (
            'if(interfaceType_par == "'
            + signal.name
            + '") begin\n'
            + leading_spaces
            + TAB_SIZE
            + signal.name
            + " = args[0];\n"
            + leading_spaces
            + "end\n"
        )
    for interface in interfaces:
        if interface.connection_mode == "native":
            curr_interface = used_interfaces[interface.type]
            for channel in interface.channels:
                if (interface.direction in ("slave", "mixed") and 
                    channel["type"] in curr_interface.master_output_channels) or (interface.direction in ("master") and 
                    channel["type"] in curr_interface.master_input_channels):
                    if ifelse_signal != "":
                        ifelse_signal += leading_spaces + "else "
                    ifelse_signal += (
                        'if(interfaceType_par == "'
                        + interface.name
                        + "_"
                        + channel["type"]
                        + '") begin\n'
                        + leading_spaces
                        + TAB_SIZE
                        + interface.name
                        + "_"
                        + channel["type"]
                        + " = args[0];\n"
                        + leading_spaces
                        + "end\n"
                    )
    testbench = include.replace_in_testbenches(testbench, "SONAR_IF_ELSE_SIGNAL", ifelse_signal[:-1])
    return testbench

def set_interfaces(testbench_config, testbench, used_interfaces):
    dut = testbench_config.modules["DUT"]
    interfaces_slave = dut.ports.get_interfaces("slave")
    interfaces_master = dut.ports.get_interfaces("master")
    interfaces_mixed = dut.ports.get_interfaces("mixed")

    replace_str = ""
    leading_spaces = include.get_indentation("SONAR_ELSE_IF_INTERFACE_IN", testbench)
    for interface in interfaces_slave:
        curr_interface = used_interfaces[interface.type]
        if replace_str != "":
            replace_str += leading_spaces
        replace_str += (
            'else if(interfaceType_par == "' + interface.name + '") begin\n'
        )
        replace_str = include.command_var_replace(
            replace_str,
            interface,
            curr_interface.master_action,
            leading_spaces + TAB_SIZE,
            curr_interface.sv_args,
        )
        replace_str += leading_spaces + "end\n"
    for interface in interfaces_mixed:
        curr_interface = used_interfaces[interface.type]
        if replace_str != "":
            replace_str += leading_spaces
        replace_str += (
            'else if(interfaceType_par == "' + interface.name + '") begin\n'
        )
        for mode in curr_interface.sv_interface_io:
            replace_str += (
                leading_spaces
                + TAB_SIZE
                + "if(args["
                + str(mode["arg"])
                + "] == "
                + str(mode["mode"])
                + ") begin\n"
            )
            replace_str = include.command_var_replace(
                replace_str,
                interface,
                getattr(curr_interface, mode["func"]),
                leading_spaces + TAB_SIZE + TAB_SIZE,
                curr_interface.sv_args,
            )
            replace_str += leading_spaces + TAB_SIZE + "end\n"
        replace_str += leading_spaces + "end\n"
    testbench = include.replace_in_testbenches(testbench, "SONAR_ELSE_IF_INTERFACE_IN", replace_str[:-1])

    replace_str = ""
    leading_spaces = include.get_indentation("SONAR_ELSE_IF_INTERFACE_OUT", testbench)
    for interface in interfaces_master:
        curr_interface = used_interfaces[interface.type]
        if replace_str != "":
            replace_str += leading_spaces
        replace_str += (
            'else if(interfaceType_par == "' + interface.name + '") begin\n'
        )
        replace_str = include.command_var_replace(
            replace_str,
            interface,
            curr_interface.slave_action,
            leading_spaces + TAB_SIZE,
            curr_interface.sv_args,
        )
        replace_str += leading_spaces + "end\n"
    testbench = include.replace_in_testbenches(testbench, "SONAR_ELSE_IF_INTERFACE_OUT", replace_str[:-1])
    return testbench

def create_clocks(testbench_config, testbench):
    # TODO make the initial state of the clock configurable (i.e. for diff. clocks)
    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")

    replace_str = ""
    largest_clock = ""
    largest_period = 0
    regex_int_str = re.compile(r"([0-9]+([\.][0-9]+)*)([a-z]+)")
    leading_spaces = include.get_indentation("SONAR_INITIAL_CLOCK", testbench)
    for clock in clocks_in:
        if replace_str != "":
            replace_str += leading_spaces
        replace_str += "initial begin\n"
        replace_str += leading_spaces + TAB_SIZE + clock.name + " = 0;\n"
        replace_str += leading_spaces + TAB_SIZE + "forever begin\n"
        replace_str += (
            leading_spaces
            + TAB_SIZE
            + TAB_SIZE
            + "#("
            + clock.period
            + "/2) "
            + clock.name
            + " <= ~"
            + clock.name
            + ";\n"
        )
        regex_match = regex_int_str.match(clock.period)
        if regex_match.group(3) == "s":
            period = regex_match.group(1) * 10 ** 15
        elif regex_match.group(3) == "ms":
            period = regex_match.group(1) * 10 ** 12
        elif regex_match.group(3) == "us":
            period = regex_match.group(1) * 10 ** 9
        elif regex_match.group(3) == "ns":
            period = regex_match.group(1) * 10 ** 6
        elif regex_match.group(3) == "ps":
            period = regex_match.group(1) * 10 ** 3
        else:
            period = regex_match.group(1)
        if int(period) > largest_period:
            largest_period = period
            largest_clock = clock.name
        replace_str += leading_spaces + TAB_SIZE + "end\n"
        replace_str += leading_spaces + "end\n"
    testbench = include.replace_in_testbenches(testbench, "SONAR_INITIAL_CLOCK", replace_str[:-1])
    testbench = include.replace_in_testbenches(testbench, "SONAR_VECTOR_CLOCK", largest_clock)

    return testbench

def set_waits(testbench_config, testbench):
    # TODO need to handle this if wait_conditions is empty (sv will error out)
    wait_conditions = include.get_from_dut(testbench_config, "wait_conditions")

    replace_str = ""
    leading_spaces = include.get_indentation("SONAR_IF_ELSE_WAIT", testbench)
    for condition in wait_conditions:
        if replace_str != "":
            replace_str += leading_spaces + "else "
        replace_str += 'if(interfaceType_par == "' + condition["key"] + '") begin\n'
        condition_str = condition["condition"].replace("$value", "args[0]")
        if not condition_str.endswith(";"):
            condition_str += ";"
        replace_str += leading_spaces + TAB_SIZE + condition_str + "\n"
        replace_str += leading_spaces + "end\n"
    testbench = include.replace_in_testbenches(testbench, "SONAR_IF_ELSE_WAIT", replace_str[:-1])

    return testbench

def count_commands(commands):
    sv_commands = [
        "delay",
        "wait",
        "signal",
        "end",
        "timestamp",
        "display",
        "flag",
        "interface"
    ]

    count = 0
    for command in commands:
        for sv_command in sv_commands:
            if sv_command in command:
                count += 1
                break
            if "macro" in command and command["macro"] == "INIT_SIGNALS":
                count += len(command["commands"])
                break
            if "macro" in command and command["macro"] == "END":
                count += 1
                break
    return count

def write_line(data_file, command, vector_id):
    if "interface" in command:
        curr_interface = include.get_interface(command["interface"]["type"])
        line = curr_interface.write_sv(command["interface"])
        if line != "":
            data_file.append(line)
    elif "wait" in command:
        if "value" in command["wait"]:
            arg = command["wait"]["value"]
        else:
            arg = 0
        data_file.append(
            "wait "
            + str(command["wait"]["key"])
            + " "
            + str(1)
            + " "
            + str(arg)
        )
    elif "signal" in command:
        data_file.append(
            "signal "
            + str(command["signal"]["name"])
            + " "
            + str(1)
            + " "
            + str(command["signal"]["value"])
        )
    elif "delay" in command:
        data_file.append(
            "delay "
            + "ns"
            + " "
            + str(1)
            + " "
            + str(command["delay"][:-2]) # TODO fix. Assumes ns
        )
    elif "display" in command:
        data_file.append(
            "display \""
            + str(command["display"])
            + "\" "
            + str(1)
            + " "
            + "0"
        )
    elif "call_dut" in command:
        pass
    elif "flag" in command:
        if "set_flag" in command["flag"]:
            data_file.append(
                "flag "
                + "set"
                + " "
                + str(1)
                + " "
                + str(command["flag"]["set_flag"])
            )
        else:
            data_file.append(
                "flag "
                + "clear"
                + " "
                + str(1)
                + " "
                + str(command["flag"]["clear_flag"])
            )
    elif "timestamp" in command:
        data_file.append(
            "timestamp "
            + str(command["timestamp"])
            + " "
            + str(1)
            + " "
            + str(0)
        )
    elif "macro" in command:
        if command["macro"] == "END":
            data_file.append(
                "end "
                + "Vector_" + str(vector_id)
                + " "
                + str(1)
                + " "
                + str(0)
            )
        else:
            for init_command in command["commands"]:
                data_file = write_line(data_file, init_command, vector_id)
    else:
        logger.error("Unhandled packet type: %s", str(command))

    return data_file

################################################################################
### calculateSeeks ###
# This function repeats over the generated data file for systemverilog and
# calculates the character counts for the different packets/parallel sections so
# the fseek function can work properly during readback. It's repeated until all
# the values converge to a static value.
def calculateSeeks(testData_sv, repeatCount, updateStr, seekStr, countStr, converged):
    i = 0
    while i < repeatCount:
        charCount = 0
        continueCount = 0
        sectionFound = False
        continueCount2 = 0
        indexToEdit = 0
        oldSize = 0
        updated = False
        currentSectionCount = 0
        cumulativeSectionCount = 0
        for index, line in enumerate(testData_sv, 0):
            charCount += len(line)
            if updateStr is not None and line.startswith(updateStr):
                currentSectionCount = int(line.split()[2])  # store the # of sections
                cumulativeSectionCount += currentSectionCount
            elif line.startswith(seekStr) and not sectionFound:
                if continueCount2 < i:
                    continueCount2 += 1
                else:
                    oldSize = int(line.split()[2])
                    sectionFound = True
                    updated = True
                    indexToEdit = index
            elif line.startswith(countStr) and sectionFound and updated:
                # This is needed to handle that there will be multiple parallel
                # sections for each test vector and to ignore the first set(s)
                # when looking at the next set
                # if cumulativeSectionCount - currentSectionCount > 0:
                #     modulo = cumulativeSectionCount - currentSectionCount
                # else:
                #     modulo = repeatCount

                # if continueCount < i % (modulo):
                #     continueCount += 1
                if cumulativeSectionCount - currentSectionCount > 0:
                    modulo = i - cumulativeSectionCount + currentSectionCount
                else:
                    modulo = i

                if continueCount < modulo:
                    continueCount += 1
                else:
                    # account for new line characters and remove current line
                    sizeDiff = index - len(line) + charCount
                    if oldSize != sizeDiff:
                        converged = False
                    testData_sv[indexToEdit] = seekStr + " " + str(sizeDiff)
                    i += 1
                    continueCount = 0
                    updated = False
                    # break
    return testData_sv, converged

def write_data_file(testbench_config):
    data_file = []
    vector_num = len(testbench_config.vectors)
    data_file.append("TestVector count " + str(vector_num))
    for _ in range(vector_num):
        data_file.append("TestVector seek 0")

    abs_thread_num = 0
    max_threads = 0
    for i, vector in enumerate(testbench_config.vectors):
        thread_num = len(vector.threads)
        abs_thread_num += thread_num
        data_file.append("ParallelSection count " + str(thread_num))
        if thread_num > max_threads:
            max_threads = thread_num
        for _ in range(thread_num):
            data_file.append("ParallelSection seek 0")
        for thread in vector.threads:
            count = count_commands(thread.commands)
            data_file.append("Packet count " + str(count))
            for packet in thread.commands:
                data_file = write_line(data_file, packet, i)

    converged1 = False
    converged2 = False
    while not (converged1 and converged2):
        converged1 = True
        converged2 = True
        testData_sv, converged1 = calculateSeeks(
            data_file,
            vector_num,
            None,
            "TestVector seek",
            "ParallelSection count",
            converged1,
        )
        data_file, converged2 = calculateSeeks(
            data_file,
            abs_thread_num,
            "ParallelSection count",
            "ParallelSection seek",
            "Packet count",
            converged2,
        )

    return data_file, max_threads

def create_testbench(testbench_config, testbench, directory):
    testbench = include.set_metadata(testbench_config, testbench)
    testbench = add_headers(testbench_config, testbench)
    testbench = add_timeformat(testbench_config, testbench)

    testbench = include.replace_in_testbenches(testbench, "SONAR_CURR_DATE", datetime.datetime.now())
    testbench = include.replace_in_testbenches(testbench, "SONAR_DATA_FILE", '"' + os.path.join(directory, f'{testbench_config.metadata["Module_Name"]}_sv.dat"'))
    testbench = include.replace_in_testbenches(testbench, "SONAR_MAX_VECTORS", len(testbench_config.vectors))

    used_interfaces = {}
    interfaces = include.get_from_dut(testbench_config, "interfaces")
    for interface in interfaces:
        try:
            used_interfaces[interface.type] = include.get_interface(interface.type)
        except ImportError as ex:
            logger.error("Interface %s not found in sonar", interface.type)
            raise SonarInvalidArgError from ex
        # if interface.type not in interface_indices:
        #     interface_indices[interface.type] = 0
        # else:
        #     interface_indices[interface.type] += 1
        # # portCopy = interface.copy()
        # # for channel in portCopy["channels"]:
        # #     if "size" not in channel:
        # #         channel["size"] = 1
        # # if "connection_mode" not in portCopy:
        # #     portCopy["connection_mode"] = "native"
        # interfaces[direction][index]["index"] = interface_indices[interface.type]
        # if hasattr(used_interfaces[interface.type], "yaml_top"):
        #     interfaces[direction][index]["index"] = used_interfaces[interface.type].yaml_top(interface)

    testbench = add_imports(testbench_config, testbench, used_interfaces)
    testbench = add_initial_prologue(testbench_config, testbench, used_interfaces)
    testbench = add_exerciser_prologue(testbench_config, testbench, used_interfaces)
    add_tcl(testbench_config, used_interfaces, directory)

    testbench, testbench_config = add_exerciser_ports(testbench_config, testbench, used_interfaces)
    testbench = instantiate_dut(testbench_config, testbench)
    testbench = instantiate_exerciser(testbench_config, testbench)
    testbench = instantiate_interface_ips(testbench_config, testbench, used_interfaces)
    testbench = declare_signals(testbench_config, testbench)
    testbench = set_signals(testbench_config, testbench, used_interfaces)
    testbench = set_interfaces(testbench_config, testbench, used_interfaces)
    testbench = create_clocks(testbench_config, testbench)
    testbench = set_waits(testbench_config, testbench)

    data_file, max_threads = write_data_file(testbench_config)

    max_args = 0
    for line in data_file:
        first_word = line.split(" ")[0]
        if first_word not in ["TestVector", "ParallelSection", "Packet"]:
            arg_count = int(quoteSplit(line)[2])
            if arg_count > max_args:
                max_args = arg_count

    testbench = include.replace_in_testbenches(testbench, "SONAR_MAX_ARG_NUM", max_args)
    testbench = include.replace_in_testbenches(testbench, "SONAR_MAX_PARALLEL", max_threads)

    return testbench, "\n".join(data_file)
