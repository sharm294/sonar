"""
The SystemVerilog backend for generating testbenches
"""

import datetime
import itertools
import logging
import os
import re
from shlex import split as quoteSplit

import sonar.core.backends.include as include
import sonar.core.backends.sv_interfaces as sv_interfaces
from sonar.exceptions import SonarInvalidArgError

logger = logging.getLogger(__name__)


def add_timeformat(testbench_config, testbench):
    """
    Configure the time format for the testbench

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Raises:
        SonarInvalidArgError: Invalid time format

    Returns:
        str: Updated testbench
    """
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
        logger.error(
            "Unknown time format: %s", testbench_config.metadata["Time_Format"]
        )
        raise SonarInvalidArgError
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_TIMEFORMAT", time_format_str
    )
    return testbench


def add_exerciser_ports(testbench_config, testbench, used_interfaces):
    """
    Add the ports of the Exerciser

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated
        used_interfaces (dict): Each used interface appears once

    Returns:
        str: Updated testbench
    """

    def add_interfaces(exerciser_ports):
        interfaces = testbench_config.get_from_dut("interfaces_dict")
        for direction in ["slave", "master", "mixed"]:
            for interface in interfaces[direction]:
                curr_interface = used_interfaces[interface.interface_type]
                for signal_type, signal in interface.signals.items():
                    exerciser_ports += leading_spaces
                    if direction in ["slave", "mixed"]:
                        if signal_type in curr_interface.signals["input"]:
                            exerciser_ports += "input "
                        else:
                            exerciser_ports += "output "
                            init_signals.append(
                                interface.name + "_" + signal_type
                            )
                    else:
                        if signal_type in curr_interface.signals["output"]:
                            exerciser_ports += "input "
                        else:
                            exerciser_ports += "output "
                            init_signals.append(
                                interface.name + "_" + signal_type
                            )
                    exerciser_ports += "logic "
                    if int(signal.size) != 1:
                        exerciser_ports += (
                            "[" + str(int(signal.size) - 1) + ":0] "
                        )
                    exerciser_ports += (
                        interface.name + "_" + signal_type + ",\n"
                    )
        return exerciser_ports

    def resolve_init_signals():
        init_commands = []
        for init_signal in init_signals:
            init_commands.append({"signal": {"name": init_signal, "value": 0}})

        for i, vector in enumerate(testbench_config.vectors):
            for j, thread in enumerate(vector.threads):
                for k, command in enumerate(thread.commands):
                    if (
                        "macro" in command
                        and command["macro"] == "INIT_SIGNALS"
                    ):
                        testbench_config.vectors[i].threads[j].commands[k][
                            "commands"
                        ] = init_commands

    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")
    signals_in = dut.ports.get_signals("input")
    resets_in = dut.ports.get_resets("input")
    signals_out = dut.ports.get_signals("output")

    init_signals = []

    exerciser_ports = ""
    leading_spaces = include.get_indentation(
        "SONAR_EXERCISER_PORTS", testbench
    )
    for clock in clocks_in:
        if exerciser_ports != "":
            exerciser_ports += leading_spaces
        exerciser_ports += "output logic " + clock.name + ",\n"

    exerciser_ports = add_interfaces(exerciser_ports)

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
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_EXERCISER_PORTS", exerciser_ports[:-2]
    )

    resolve_init_signals()

    return testbench, testbench_config


def instantiate_exerciser(testbench_config, testbench):
    """
    Instantiate the Exerciser module

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Returns:
        str: Updated testbench
    """
    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")
    signals = dut.ports.get_signals()
    resets = dut.ports.get_resets()
    interfaces = testbench_config.get_from_dut("interfaces")

    exerciser_int = ""
    leading_spaces = include.get_indentation("SONAR_EXERCISER_INT", testbench)
    exerciser_int += "exerciser exerciser_i(\n"
    for clock in clocks_in:
        exerciser_int += (
            leading_spaces
            + include.TAB_SIZE
            + "."
            + clock.name
            + "("
            + clock.name
            + "),\n"
        )
    for interface in interfaces:
        for signal_type, signal in interface.signals.items():
            exerciser_int += (
                leading_spaces
                + include.TAB_SIZE
                + "."
                + interface.name
                + "_"
                + signal_type
                + "("
                + interface.name
                + "_"
                + signal_type
                + "),\n"
            )
    for signal in itertools.chain(signals, resets):
        exerciser_int += (
            leading_spaces
            + include.TAB_SIZE
            + "."
            + signal.name
            + "("
            + signal.name
            + "),\n"
        )
    exerciser_int = exerciser_int[:-2] + "\n"
    exerciser_int += leading_spaces + ");\n"
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_EXERCISER_INT", exerciser_int[:-1]
    )
    return testbench


def modify_signal_name(original_name, dut_type):
    """
    For Vivado HLS, some signal names are changed from the source file in the
    generated Verilog. Here, we address that change

    Args:
        original_name (str): The original name of the port from the src file
        dut_type (dict): Information from the testbench config describing the
        type of DUT that is being used.

    Returns:
        str: The modified name of the signal, if changed
    """
    port_name = original_name
    if dut_type["lang"] != "sv":  # TODO temporary workaround
        if dut_type["hls"] == "vivado" and dut_type["hls_version"] == "2018.1":
            port_name = original_name + "_V"
    return port_name


def instantiate_dut(testbench_config, testbench):
    """
    Instantiate the device-under-test

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Returns:
        str: Updated testbench
    """
    # pylint: disable=too-many-locals
    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")
    signals_in = dut.ports.get_signals("input")
    resets_in = dut.ports.get_resets("input")
    signals_out = dut.ports.get_signals("output")
    parameters = testbench_config.get_from_dut("parameters")
    interfaces = testbench_config.get_from_dut("interfaces")

    dut_inst = ""
    leading_spaces = include.get_indentation("SONAR_DUT_INST", testbench)
    module_name = testbench_config.metadata["Module_Name"]
    if parameters:
        dut_inst += testbench_config.metadata["Module_Name"] + " #(\n"
        for parameter in parameters[:-1]:
            dut_inst += f"{leading_spaces}{include.TAB_SIZE}.{parameter[0]}({str(parameter[1])}),\n"
        dut_inst += f"{leading_spaces}{include.TAB_SIZE}.{parameters[-1][0]}({str(parameters[-1][1])})\n"
        dut_inst += f"{leading_spaces}) {module_name}_i (\n"
    else:
        dut_inst += f"{module_name} {module_name}_i (\n"
    for signal in itertools.chain(clocks_in, resets_in):
        dut_inst += f"{leading_spaces}{include.TAB_SIZE}.{signal.name}({signal.name}),\n"
    dut_type = testbench_config.modules["DUT"].type
    for signal in itertools.chain(signals_in, signals_out):
        port_name = modify_signal_name(signal.name, dut_type)
        dut_inst += (
            f"{leading_spaces}{include.TAB_SIZE}.{port_name}({signal.name}),\n"
        )
    for interface in interfaces:
        for signal_type, signal in interface.signals.items():
            dut_inst += (
                leading_spaces
                + include.TAB_SIZE
                + "."
                + interface.name
                + "_"
                + signal.name
                + "("
                + interface.name
                + "_"
                + signal_type
                + "),\n"
            )
    dut_inst = dut_inst[:-2] + "\n"
    dut_inst += leading_spaces + ");"
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_DUT_INST", dut_inst
    )

    return testbench


def declare_signals(testbench_config, testbench):
    """
    Declare all signals used to connect to the DUT

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Returns:
        str: Updated testbench
    """
    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")
    signals = dut.ports.get_signals()
    resets = dut.ports.get_resets()
    interfaces = testbench_config.get_from_dut("interfaces")

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
        for signal_type, signal in interface.signals.items():
            if int(signal.size) == 1:
                tb_signal_list += (
                    leading_spaces
                    + "logic "
                    + interface.name
                    + "_"
                    + signal_type
                    + ";\n"
                )
            else:
                tb_signal_list += (
                    leading_spaces
                    + "logic ["
                    + str(int(signal.size) - 1)
                    + ":0] "
                    + interface.name
                    + "_"
                    + signal_type
                    + ";\n"
                )
            if int(signal.size) > max_signal_size:
                max_signal_size = int(signal.size)
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_TB_SIGNAL_LIST", tb_signal_list[:-1]
    )
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_MAX_DATA_SIZE", max_signal_size
    )
    return testbench


def set_signals(testbench_config, testbench, used_interfaces):
    """
    When reading commands, add the logic to assign values to individual signals

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated
        used_interfaces (dict): Each used interface appears once

    Returns:
        str: Updated testbench
    """
    dut = testbench_config.modules["DUT"]
    signals_in = dut.ports.get_signals("input")
    resets_in = dut.ports.get_resets("input")
    interfaces = testbench_config.get_from_dut("interfaces")

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
            + include.TAB_SIZE
            + signal.name
            + " = args[0];\n"
            + leading_spaces
            + "end\n"
        )
    for interface in interfaces:
        curr_interface = used_interfaces[interface.interface_type]
        for signal_type, signal in interface.signals.items():
            if (
                interface.direction in ("slave", "mixed")
                and signal_type in curr_interface.signals["output"]
            ) or (
                interface.direction in ("master")
                and signal_type in curr_interface.signals["input"]
            ):
                if ifelse_signal != "":
                    ifelse_signal += leading_spaces + "else "
                ifelse_signal += (
                    'if(interfaceType_par == "'
                    + interface.name
                    + "_"
                    + signal_type
                    + '") begin\n'
                    + leading_spaces
                    + include.TAB_SIZE
                    + interface.name
                    + "_"
                    + signal_type
                    + " = args[0];\n"
                    + leading_spaces
                    + "end\n"
                )
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_IF_ELSE_SIGNAL", ifelse_signal[:-1]
    )
    return testbench


def set_interfaces(testbench_config, testbench):
    """
    When reading commands, add the logic to assign interact with interfaces

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Returns:
        str: Updated testbench
    """
    interfaces = testbench_config.get_from_dut("interfaces")

    replace_str = ""
    leading_spaces = include.get_indentation(
        "SONAR_ELSE_IF_INTERFACE_IN", testbench
    )
    for index, interface in enumerate(interfaces):
        if replace_str != "":
            replace_str += leading_spaces
        replace_str += 'else if(interfaceType_par == "$$name") begin\n'
        replace_str += (
            leading_spaces
            + include.TAB_SIZE
            + f"$$interfaceType_$$index(args, retval[{index}]);\n"
        )
        replace_str += (
            leading_spaces
            + include.TAB_SIZE
            + f"if(retval[{index}] != 0) begin\n"
        )
        replace_str += (
            leading_spaces + include.TAB_SIZE * 2 + "error = 1'b1;\n"
        )
        replace_str += leading_spaces + include.TAB_SIZE * 2 + "$stop;\n"
        replace_str += leading_spaces + include.TAB_SIZE + "end\n"
        replace_str += leading_spaces + "end\n"
        replace_str = include.replace_variables(replace_str, interface)
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_ELSE_IF_INTERFACE_IN", replace_str[:-1]
    )
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_INTERFACES_COUNT", len(interfaces)
    )
    return testbench


def create_clocks(testbench_config, testbench):
    """
    Create clocks used in the testbench

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Returns:
        str: Updated testbench
    """
    # TODO make the initial state of the clock configurable (i.e. for diff. clocks)
    dut = testbench_config.modules["DUT"]
    clocks_in = dut.ports.get_clocks("input")

    largest_clock = ""
    largest_period = 0
    regex_int_str = re.compile(r"([0-9]+([\.][0-9]+)*)([a-z]+)")
    for clock in clocks_in:
        regex_match = regex_int_str.match(clock.period)
        if regex_match.group(3) == "s":
            period = float(regex_match.group(1)) * 10 ** 15
        elif regex_match.group(3) == "ms":
            period = float(regex_match.group(1)) * 10 ** 12
        elif regex_match.group(3) == "us":
            period = float(regex_match.group(1)) * 10 ** 9
        elif regex_match.group(3) == "ns":
            period = float(regex_match.group(1)) * 10 ** 6
        elif regex_match.group(3) == "ps":
            period = float(regex_match.group(1)) * 10 ** 3
        else:
            period = float(regex_match.group(1))
        if period > largest_period:
            largest_period = period
            largest_clock = clock.name
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_VECTOR_CLOCK", largest_clock
    )

    return testbench


def set_waits(testbench_config, testbench):
    """
    Add the logic to handle wait conditions

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Returns:
        str: Updated testbench
    """
    # TODO need to handle this if wait_conditions is empty (sv will error out)
    wait_conditions = testbench_config.get_from_dut("wait_conditions")

    replace_str = ""
    leading_spaces = include.get_indentation("SONAR_IF_ELSE_WAIT", testbench)
    for condition in wait_conditions:
        if replace_str != "":
            replace_str += leading_spaces + "else "
        replace_str += (
            'if(interfaceType_par == "' + condition["key"] + '") begin\n'
        )
        regex_variable = re.compile(r"\$\d+")
        condition_str = condition["condition"]
        variables = re.findall(regex_variable, condition["condition"])
        for variable in variables:
            condition_str = condition_str.replace(
                variable, f"args[{variable[1:]}]"
            )
        if not condition_str.endswith(";"):
            condition_str += ";"
        replace_str += leading_spaces + include.TAB_SIZE + condition_str + "\n"
        replace_str += leading_spaces + "end\n"
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_IF_ELSE_WAIT", replace_str[:-1]
    )

    return testbench


def count_commands(commands):
    """
    Count the number of actual commands from a list of commands that may contain
    "macro" commands

    Args:
        commands (list): List of commands

    Returns:
        int: The true number of commands
    """
    sv_commands = [
        "delay",
        "wait",
        "signal",
        "end",
        "timestamp",
        "display",
        "flag",
    ]

    count = 0
    for command in commands:
        for sv_command in sv_commands:
            if sv_command in command:
                count += 1
                break
            if "interface" in command:
                count += len(command["interface"]["payload"])
                break
            if "macro" in command and command["macro"] == "INIT_SIGNALS":
                count += len(command["commands"])
                break
            if "macro" in command and command["macro"] == "END":
                count += 1
                break
    return count


def write_line(data_file, command, vector_id):
    """
    Write one command to the data file

    Args:
        data_file (list): List of commands to write
        command (dict): Current command being written
        vector_id (int): Index of the test vector this command belongs to

    Returns:
        list: Updated data_file
    """
    # pylint: disable=too-many-branches
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
        txt = "wait " + command["wait"]["key"] + " "
        if "args" in command["wait"] and command["wait"]["args"]:
            txt += str(len(command["wait"]["args"]))
            for arg in command["wait"]["args"]:
                txt += " " + str(arg)
        else:
            txt += "0"
        data_file.append(txt)
    elif "signal" in command:
        # TODO temporary hack for endpoint assignment
        if "value2" in command["signal"]:
            data_file.append(
                "signal "
                + str(command["signal"]["name"])
                + " "
                + str(2)
                + " "
                + str(command["signal"]["value"])
                + " "
                + str(command["signal"]["value2"])
            )
        else:
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
            + str(command["delay"][:-2])  # TODO fix. Assumes ns
        )
    elif "display" in command:
        data_file.append(
            'display "' + str(command["display"]) + '" ' + str(1) + " " + "0"
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
                + "Vector_"
                + str(vector_id)
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


# TODO this is a fairly magic function, should probably make more understandable
def calculate_seeks(
    data_file, max_repeat, update_str, seek_str, count_str, converged
):
    """
    This function repeats over the generated data file for systemverilog and
    calculates the character counts for the different packets/parallel sections
    so the fseek function can work properly during readback. It's repeated
    until all the values converge to a static value.

    Args:
        data_file (list): List of commands
        max_repeat (int): Maximum number of times to repeat without convergence
        update_str (str): ???
        seek_str (str): ???
        count_str (str): ???
        converged (bool): True if the sizes converge

    Returns:
        tuple(list, bool): The data file and converged state
    """
    # pylint: disable=too-many-locals
    i = 0
    while i < max_repeat:
        char_count = 0
        continue_count = 0
        section_found = False
        continue_count_2 = 0
        index_to_edit = 0
        old_size = 0
        updated = False
        curr_section_count = 0
        cumulative_section_count = 0
        for index, line in enumerate(data_file, 0):
            char_count += len(line)
            if update_str is not None and line.startswith(update_str):
                curr_section_count = int(
                    line.split()[2]
                )  # store the # of sections
                cumulative_section_count += curr_section_count
            elif line.startswith(seek_str) and not section_found:
                if continue_count_2 < i:
                    continue_count_2 += 1
                else:
                    old_size = int(line.split()[2])
                    section_found = True
                    updated = True
                    index_to_edit = index
            elif line.startswith(count_str) and section_found and updated:
                # This is needed to handle that there will be multiple parallel
                # sections for each test vector and to ignore the first set(s)
                # when looking at the next set
                # if cumulative_section_count - curr_section_count > 0:
                #     modulo = cumulative_section_count - curr_section_count
                # else:
                #     modulo = max_repeat

                # if continue_count < i % (modulo):
                #     continue_count += 1
                if cumulative_section_count - curr_section_count > 0:
                    modulo = i - cumulative_section_count + curr_section_count
                else:
                    modulo = i

                if continue_count < modulo:
                    continue_count += 1
                else:
                    # account for new line characters and remove current line
                    size_diff = index - len(line) + char_count
                    if old_size != size_diff:
                        converged = False
                    data_file[index_to_edit] = seek_str + " " + str(size_diff)
                    i += 1
                    continue_count = 0
                    updated = False
                    # break
    return data_file, converged


def write_data_file(testbench_config):
    """
    Write the data file

    Args:
        testbench_config (Testbench): The testbench configuration

    Returns:
        tuple(list, int): The data file commands as a list and max number of
            threads in any one test vector
    """
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
        data_file, converged1 = calculate_seeks(
            data_file,
            vector_num,
            None,
            "TestVector seek",
            "ParallelSection count",
            converged1,
        )
        data_file, converged2 = calculate_seeks(
            data_file,
            abs_thread_num,
            "ParallelSection count",
            "ParallelSection seek",
            "Packet count",
            converged2,
        )

    return data_file, max_threads


def create_testbench(testbench_config, testbench, directory):
    """
    Create the testbench for this language backend

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated
        directory (str): Path to the directory to place generated files

    Returns:
        Tuple(str, str): The testbench and the data file
    """
    testbench = include.set_metadata(testbench_config, testbench)
    testbench = add_timeformat(testbench_config, testbench)

    testbench = include.replace_in_testbenches(
        testbench, "SONAR_CURR_DATE", datetime.datetime.now()
    )
    testbench = include.replace_in_testbenches(
        testbench,
        "SONAR_DATA_FILE",
        '"'
        + os.path.join(
            directory, f'{testbench_config.metadata["Module_Name"]}_sv.dat"'
        ),
    )
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_MAX_VECTORS", len(testbench_config.vectors)
    )

    used_interfaces = {}
    interfaces = testbench_config.get_from_dut("interfaces")
    for interface in interfaces:
        used_interfaces[interface.interface_type] = include.get_interface(
            interface.interface_type
        )

    testbench, testbench_config = add_exerciser_ports(
        testbench_config, testbench, used_interfaces
    )
    testbench = instantiate_dut(testbench_config, testbench)
    testbench = instantiate_exerciser(testbench_config, testbench)

    testbench = declare_signals(testbench_config, testbench)
    testbench = set_signals(testbench_config, testbench, used_interfaces)
    testbench = set_interfaces(testbench_config, testbench)
    testbench = create_clocks(testbench_config, testbench)

    testbench = set_waits(testbench_config, testbench)

    testbench = sv_interfaces.add_signal_endpoints(testbench_config, testbench)
    testbench = sv_interfaces.add_interfaces(
        testbench_config, testbench, directory
    )

    data_file, max_threads = write_data_file(testbench_config)

    max_args = 0
    for line in data_file:
        first_word = line.split(" ")[0]
        if first_word not in ["TestVector", "ParallelSection", "Packet"]:
            arg_count = int(quoteSplit(line)[2])
            if arg_count > max_args:
                max_args = arg_count

    testbench = include.replace_in_testbenches(
        testbench, "SONAR_MAX_ARG_NUM", max_args
    )
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_MAX_PARALLEL", max_threads
    )

    return testbench, "\n".join(data_file)
