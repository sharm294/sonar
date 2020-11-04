"""
The C++ backend for generating testbenches
"""

import itertools
import logging
import os
from shlex import split as quoteSplit

import sonar.core.backends.include as include
from sonar.interfaces.axi4_lite_slave import AXI4LiteSlave
from sonar.interfaces.axi4_stream import AXI4Stream

TAB_SIZE = "    "

logger = logging.getLogger(__name__)


def declare_signals(testbench_config, testbench):
    """
    Declare and instantiate the variables used for the signals in the testbench

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Returns:
        str: Updated testbench
    """
    dut = testbench_config.modules["DUT"]
    signals = dut.ports.get_signals()
    interfaces = testbench_config.get_from_dut("interfaces")

    tb_signal_list = ""
    max_signal_size = 0
    leading_spaces = include.get_indentation("SONAR_TB_SIGNAL_LIST", testbench)
    for signal in signals:
        # TODO fix leading spaces on first entry
        tb_signal_list += (
            leading_spaces
            + "ap_uint<"
            + str(signal.size)
            + "> "
            + signal.name
            + ";\n"
        )
        if int(signal.size) > max_signal_size:
            max_signal_size = int(signal.size)
    for interface in interfaces:
        if isinstance(interface, AXI4LiteSlave):
            data_width_c = interface.get_signal("wdata").size
            for regs in interface.registers:
                tb_signal_list += (
                    leading_spaces + f"ap_uint<{data_width_c}> {regs};\n"
                )
        elif isinstance(interface, AXI4Stream):
            tb_signal_list += (
                leading_spaces
                + interface.iClass
                + " "
                + interface.name
                + ";\n"
            )
            tb_signal_list += (
                leading_spaces
                + interface.flit
                + " "
                + interface.name
                + "_flit;\n"
            )
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_TB_SIGNAL_LIST", tb_signal_list[:-1]
    )
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_MAX_DATA_SIZE", max_signal_size
    )
    return testbench


def set_signals(testbench_config, testbench):
    """
    Add commands to interact with signals when reading the data file

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Returns:
        str: Updated testbench
    """
    dut = testbench_config.modules["DUT"]
    signals_in = dut.ports.get_signals("input")

    ifelse_signal = ""
    leading_spaces = include.get_indentation("SONAR_IF_ELSE_SIGNAL", testbench)

    for signal in signals_in:
        if "type" not in signal:
            if ifelse_signal != "":
                ifelse_signal += leading_spaces + "else "
            ifelse_signal += (
                'if(!strcmp(interfaceType, "' + signal.name + '")){\n'
            )
            ifelse_signal += (
                leading_spaces + TAB_SIZE + signal.name + " = args[0];\n"
            )
            ifelse_signal += leading_spaces + "}\n"

    # TODO fix this
    # ifelse_signal = ""  # clear this since it's not being used right now

    testbench = include.replace_in_testbenches(
        testbench, "SONAR_IF_ELSE_SIGNAL", ifelse_signal[:-1]
    )
    return testbench


def set_interfaces(testbench_config, testbench):
    """
    Add commands to interact with interfaces when reading the data file

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated

    Returns:
        str: Updated testbench
    """
    dut = testbench_config.modules["DUT"]
    interfaces_slave = dut.ports.get_interfaces("slave")
    interfaces_master = dut.ports.get_interfaces("master")
    interfaces_mixed = dut.ports.get_interfaces("mixed")

    replace_str = ""
    leading_spaces = include.get_indentation(
        "SONAR_ELSE_IF_INTERFACE_IN", testbench
    )
    for interface in itertools.chain(interfaces_slave, interfaces_mixed):
        if replace_str != "":
            replace_str += leading_spaces + "else "
        replace_str += (
            'if(!strcmp(interfaceType, "' + interface.name + '")){\n'
        )
        replace_str = include.command_var_replace(
            replace_str, interface, leading_spaces + TAB_SIZE, "cpp", "master"
        )
        replace_str += leading_spaces + "}\n"
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_ELSE_IF_INTERFACE_IN", replace_str[:-1]
    )

    replace_str_2 = ""
    leading_spaces = include.get_indentation(
        "SONAR_ELSE_IF_INTERFACE_OUT", testbench
    )
    for interface in interfaces_master:
        if replace_str != "" or replace_str_2 != "":
            replace_str_2 += (
                leading_spaces + "else "
            )  # TODO fix this on first one. too many spaces
        replace_str_2 += (
            'if(!strcmp(interfaceType, "' + interface.name + '")){\n'
        )
        replace_str_2 = include.command_var_replace(
            replace_str_2, interface, leading_spaces + TAB_SIZE, "cpp", "slave"
        )
        replace_str_2 += leading_spaces + "}\n"
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_ELSE_IF_INTERFACE_OUT", replace_str_2[:-1]
    )
    return testbench


def write_line(data_file, command, vector_id):
    """
    Write one line to the data file

    Args:
        data_file (list): List of commands for the data file
        command (dict): Current command to write
        vector_id (int): Index of the current test vector

    Returns:
        list: Updated data_file
    """
    if "interface" in command:
        curr_interface = include.get_interface(command["interface"]["type"])
        line = curr_interface.write_cpp(command["interface"])
        if line != "":
            data_file.append(line)
    elif "wait" in command:
        pass
    elif "signal" in command:
        # data_file.append(
        #     "signal "
        #     + str(command["signal"]["name"])
        #     + " "
        #     + str(1)
        #     + " "
        #     + str(command["signal"]["value"])
        # )
        pass
    elif "delay" in command:
        pass
    elif "display" in command:
        data_file.append(
            'display "' + str(command["display"]) + '" ' + "NULL 1" + " " + "0"
        )
    elif "call_dut" in command:
        data_file.append(
            "call_dut " + "NULL" + " " + "NULL 1 " + str(command["call_dut"])
        )
    elif "flag" in command:
        pass
    elif "timestamp" in command:
        data_file.append(
            "timestamp "
            + str(command["timestamp"])
            + " "
            + "NULL 1"
            + " "
            + str(0)
        )
    elif "macro" in command:
        if command["macro"] == "END":
            data_file.append(
                "end " + "Vector_" + str(vector_id) + " NULL 1 " + str(0)
            )
    else:
        logger.error("Unhandled packet type: %s", str(command))

    return data_file


def write_data_file(testbench_config):
    """
    Based on the test vectors, write the data file

    Args:
        testbench_config (Testbench): The testbench configuration

    Returns:
        list: List of commands to write to the data file
    """
    data_file = []
    for i, vector in enumerate(testbench_config.vectors):
        for thread in vector.threads:
            for command in thread.commands:
                data_file = write_line(
                    data_file,
                    command,
                    i,
                )

    data_file.append("finish NULL NULL 0 0")

    return data_file


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
    testbench = include.replace_in_testbenches(
        testbench,
        "SONAR_DATA_FILE",
        '"'
        + os.path.join(
            directory, f'{testbench_config.metadata["Module_Name"]}_cpp.dat"'
        ),
    )

    # this is currently not used: no signals can be set in cpp
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_IF_ELSE_SIGNAL", ""
    )

    # testbench = instantiate_dut(testbench_config, testbench)
    testbench = declare_signals(testbench_config, testbench)
    testbench = set_signals(testbench_config, testbench)
    testbench = set_interfaces(testbench_config, testbench)

    data_file = write_data_file(testbench_config)

    max_args = 0
    for line in data_file:
        first_word = line.split(" ")[0]
        if first_word not in ["TestVector", "ParallelSection", "Packet"]:
            arg_count = int(quoteSplit(line)[3])
            if arg_count > max_args:
                max_args = arg_count

    testbench = include.replace_in_testbenches(
        testbench, "SONAR_MAX_ARG_NUM", max_args
    )

    return testbench, "\n".join(data_file)
