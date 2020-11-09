"""
Add interfaces to SV testbenches
"""

import os

import sonar.core.backends.include as include


def add_imports(testbench_config, testbench, used_interfaces):
    """
    Import any packages that may be needed

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated
        used_interfaces (dict): Each used interface appears once

    Returns:
        str: Updated testbench
    """
    interfaces = testbench_config.get_from_dut("interfaces")

    imports = ""
    for _name, interface in used_interfaces.items():
        if hasattr(interface, "import_packages_global"):
            imports += interface.import_packages_global()
    for interface in interfaces:
        curr_interface = used_interfaces[interface.interface_type]
        if hasattr(curr_interface, "import_packages_local"):
            imports += curr_interface.import_packages_local(interface)
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_IMPORT_PACKAGES", imports[:-1]
    )
    return testbench


def add_prologue(testbench, interface):
    """
    Declare any variables that may be needed by the interface

    Args:
        testbench (str): The testbench component being generated
        interface (BaseInterface): The interface currently being looked at

    Returns:
        str: Updated testbench
    """
    if hasattr(interface.core, "prologue"):
        prologue = interface.core.prologue("")
        prologue = include.replace_variables(prologue, interface)
        testbench += prologue + "\n"
    return testbench


def add_initial_blocks(testbench, interface):
    """
    Add any statements an interface might require within an initial block

    Args:
        testbench (str): The testbench being generated
        interface (BaseInterface): The interface currently being looked at

    Returns:
        str: Updated testbench
    """
    initial_blocks = []
    if hasattr(interface.core, "initial_blocks"):
        initial_blocks_raw = interface.core.initial_blocks(include.TAB_SIZE)
        for block in initial_blocks_raw:
            initial_blocks.append(include.replace_variables(block, interface))
    for block in initial_blocks:
        testbench += "initial begin\n" + block + "end\n"
    return testbench + "\n"


def add_tcl(interface, directory):
    """
    Generates any TCL scripts as required by interfaces

    Args:
        testbench (str): The testbench being generated
        directory (str): Path to directory to place generated files
    """
    if hasattr(interface.core, "source_tcl"):
        interface.core.source_tcl(interface, directory)


def instantiate_interface_ips(testbench, interface):
    """
    Instantiate any IPs required by the interfaces

    Args:
        testbench (str): The testbench being generated
        used_interfaces (dict): Each used interface appears once

    Returns:
        str: Updated testbench
    """
    ip_inst = ""
    if hasattr(interface.core, "instantiate"):
        ip_inst = interface.core.instantiate(interface, "", include.TAB_SIZE)
    testbench += ip_inst + "\n"
    return testbench


def get_nth_index(dictionary, search_key):
    """
    From a dictionary, get the nth key

    Args:
        dictionary (dict): Dictionary to retrieve from
        search_key (str): Key to search for

    Raises:
        IndexError: Key not found

    Returns:
        int: Index of the search_key
    """
    for i, key in enumerate(dictionary):
        if key == search_key:
            return i
    raise IndexError("dictionary index out of range")


def add_interfaces(testbench_config, testbench, directory, used_interfaces):
    """
    Add interfaces and their sources/sinks

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated
        directory (str): Path to the directory to place generated files
        used_interfaces (dict): Each used interface appears once

    Returns:
        str: The testbench
    """

    testbench = add_imports(testbench_config, testbench, used_interfaces)

    endpoints = ""
    leading_spaces = include.get_indentation(
        "SONAR_INCLUDE_ENDPOINTS", testbench
    )
    interfaces = testbench_config.get_from_dut("interfaces")
    for interface in interfaces:
        interface_str = ""
        interface_str = add_prologue(interface_str, interface)
        interface_str = add_initial_blocks(interface_str, interface)
        interface_str = instantiate_interface_ips(interface_str, interface)

        for key in interface.endpoint_modes:
            # for key, _commands in interface.core.actions["sv"].items():
            interface_str += f"task $$interfaceType_$$index_{key}(input logic [MAX_DATA_SIZE-1:0] args [MAX_ARG_NUM], output int retval);\n"
            interface_str += include.TAB_SIZE + "retval = 0;\n"
            interface_str = include.command_var_replace(
                interface_str, interface, include.TAB_SIZE, "sv", key
            )
            interface_str += "endtask\n"

        index = 0
        interface_str += "task $$interfaceType_$$index(input logic [MAX_DATA_SIZE-1:0] args [MAX_ARG_NUM], output int retval);\n"
        interface_str += include.TAB_SIZE + "retval = 0;\n"
        # for key, _commands in interface.core.actions["sv"].items():
        for key in interface.endpoint_modes:
            interface_str += include.TAB_SIZE
            if index != 0:
                interface_str += "else "
            arg_index = get_nth_index(interface.core.actions["sv"], key)
            interface_str += f"if (args[0] == {arg_index}) begin\n"
            interface_str += (
                include.TAB_SIZE * 2
                + f"$$interfaceType_$$index_{key}(args, retval);\n"
            )
            interface_str += include.TAB_SIZE + "end\n"
            index += 1
        interface_str += "endtask\n"
        interface_str = include.replace_variables(interface_str, interface)

        add_tcl(interface, directory)

        filename = interface.interface_type + f"_{interface.index}.sv"
        filepath = os.path.join(directory, filename)
        with open(filepath, "w+") as f:
            f.write(interface_str)
        if endpoints != "":
            endpoints += leading_spaces
        endpoints += f'`include "{filename}"\n'

    testbench = include.replace_in_testbenches(
        testbench, "SONAR_INCLUDE_ENDPOINTS", endpoints
    )
    return testbench
