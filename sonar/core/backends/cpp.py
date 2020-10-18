import logging
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
            if header_mode == "cpp":
                headers += f'#include "{header_file}"\n'
            elif header_mode == "auto":
                if header_file.endswith((".h", ".hpp")):
                    headers += f'#include "{header_file}"\n'
    testbench = include.replace_in_testbenches(testbench, "SONAR_HEADER_FILE", headers)
    return testbench

# def instantiate_dut(testbench_config, testbench):
#     dut = testbench_config.modules["DUT"]
#     signals_in = dut.ports.get_signals("input")
#     signals_out = dut.ports.get_signals("output")
#     interfaces = include.get_from_dut(testbench_config, "interfaces_dict")

#     dut_inst = testbench_config.metadata["Module_Name"] + "("

#     for direction in ["slave", "master", "mixed"]:
#         for interface in interfaces[direction]:
#             if interface.type == "s_axilite":
#                 for regs in interface.registers:
#                     dut_inst += f"{regs}, "
#                 continue
#             if interface.type == "axis":
#                 dut_inst += "&"
#             dut_inst += interface.name + ", "
#     for signal in itertools.chain(signals_in, signals_out):
#         if signal.direction == "output":
#             dut_inst += "&"
#         dut_inst += signal.name + ", "

#     dut_inst = dut_inst[:-2] + ");"
#     testbench = include.replace_in_testbenches(testbench, "SONAR_DUT_INST", dut_inst, include_langs=["cpp"])
#     return testbench

def declare_signals(testbench_config, testbench):
    dut = testbench_config.modules["DUT"]
    signals = dut.ports.get_signals()
    interfaces = include.get_from_dut(testbench_config, "interfaces")

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
        for channel in interface.channels:
            if channel["type"] == "wdata":
                data_width_c = channel["size"]
                break
        if interface.type == "s_axilite":
            for regs in interface.registers:
                tb_signal_list += (
                    leading_spaces + f"ap_uint<{data_width_c}> {regs};\n"
                )
        elif interface.type == "axis":
            tb_signal_list += (
                leading_spaces + interface.iClass + " " + interface.name + ";\n"
            )
            tb_signal_list += (
                leading_spaces
                + interface.flit
                + " "
                + interface.name
                + "_flit;\n"
            )
    testbench = include.replace_in_testbenches(testbench, "SONAR_TB_SIGNAL_LIST", tb_signal_list[:-1])
    testbench = include.replace_in_testbenches(testbench, "SONAR_MAX_DATA_SIZE", max_signal_size)
    return testbench

def set_signals(testbench_config, testbench):
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

    testbench = include.replace_in_testbenches(testbench, "SONAR_IF_ELSE_SIGNAL", ifelse_signal[:-1])
    return testbench

def set_interfaces(testbench_config, testbench, used_interfaces):
    dut = testbench_config.modules["DUT"]
    interfaces_slave = dut.ports.get_interfaces("slave")
    interfaces_master = dut.ports.get_interfaces("master")
    interfaces_mixed = dut.ports.get_interfaces("mixed")

    replace_str = ""
    leading_spaces = include.get_indentation("SONAR_ELSE_IF_INTERFACE_IN", testbench)
    for interface in itertools.chain(interfaces_slave, interfaces_mixed):
        if replace_str != "":
            replace_str += leading_spaces + "else "
        replace_str += (
            'if(!strcmp(interfaceType, "' + interface.name + '")){\n'
        )
        curr_interface = used_interfaces[interface.type]
        replace_str = include.command_var_replace(
            replace_str,
            interface,
            curr_interface.c_interface_in,
            leading_spaces + TAB_SIZE,
            curr_interface.c_args,
        )
        replace_str += leading_spaces + "}\n"
    testbench = include.replace_in_testbenches(testbench, "SONAR_ELSE_IF_INTERFACE_IN", replace_str[:-1])

    replace_str_2 = ""
    leading_spaces = include.get_indentation("SONAR_ELSE_IF_INTERFACE_OUT", testbench)
    for interface in interfaces_master:
        if replace_str != "" or replace_str_2 != "":
            replace_str_2 += (
                leading_spaces + "else "
            )  # TODO fix this on first one. too many spaces
        replace_str_2 += (
            'if(!strcmp(interfaceType, "' + interface.name + '")){\n'
        )
        curr_interface = used_interfaces[interface.type]
        replace_str_2 = include.command_var_replace(
            replace_str_2,
            interface,
            curr_interface.c_interface_out,
            leading_spaces + TAB_SIZE,
            curr_interface.c_args,
        )
        replace_str_2 += leading_spaces + "}\n"
    testbench = include.replace_in_testbenches(testbench, "SONAR_ELSE_IF_INTERFACE_OUT", replace_str_2[:-1])
    return testbench

def write_line(data_file, command, vector_id):
    if "interface" in command:
        curr_interface = include.get_interface(command["interface"]["type"])
        line = curr_interface.write_c(command["interface"])
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
            "display \""
            + str(command["display"])
            + "\" "
            + "NULL 1"
            + " "
            + "0"
        )
    elif "call_dut" in command:
        data_file.append(
            "call_dut "
            + "NULL"
            + " "
            + "NULL 1 "
            + str(command["call_dut"])
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
    data_file = []
    for i, vector in enumerate(testbench_config.vectors):
        for j, thread in enumerate(vector.threads):
            for k, command in enumerate(thread.commands):
                if "interface" in command:
                    new_packets = []
                    curr_interface = include.get_interface(command["interface"]["type"])
                    for packet in command["interface"]["payload"]:
                        new_packets.append(curr_interface.json_payload(packet))
                    testbench_config.vectors[i].threads[j].commands[k]["payload"] = new_packets

                data_file = write_line(data_file, testbench_config.vectors[i].threads[j].commands[k], i)

    data_file.append("finish NULL NULL 0 0")

    return data_file

def create_testbench(testbench_config, testbench, directory):
    testbench = include.set_metadata(testbench_config, testbench)
    testbench = add_headers(testbench_config, testbench)
    testbench = include.replace_in_testbenches(testbench, "SONAR_DATA_FILE", '"' + os.path.join(directory, f'{testbench_config.metadata["Module_Name"]}_cpp.dat"'))

    # this is currently not used: no signals can be set in cpp
    testbench = include.replace_in_testbenches(testbench, "SONAR_IF_ELSE_SIGNAL", "")

    used_interfaces = {}
    interfaces = include.get_from_dut(testbench_config, "interfaces")
    for interface in interfaces:
        try:
            used_interfaces[interface.type] = include.get_interface(interface.type)
        except ImportError as ex:
            logger.error("Interface %s not found in sonar", interface.type)
            raise SonarInvalidArgError from ex

    # testbench = instantiate_dut(testbench_config, testbench)
    testbench = declare_signals(testbench_config, testbench)
    testbench = set_signals(testbench_config, testbench)
    testbench = set_interfaces(testbench_config, testbench, used_interfaces)

    data_file = write_data_file(testbench_config)

    max_args = 0
    for line in data_file:
        first_word = line.split(" ")[0]
        if first_word not in ["TestVector", "ParallelSection", "Packet"]:
            arg_count = int(quoteSplit(line)[3])
            if arg_count > max_args:
                max_args = arg_count

    testbench = include.replace_in_testbenches(testbench, "SONAR_MAX_ARG_NUM", max_args)

    return testbench, "\n".join(data_file)
