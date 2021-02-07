"""
Add interfaces to SV testbenches
"""

import os

import sonar.core.backends.include as include


def add_prologue(testbench, endpoint, interface):
    """
    Declare any variables that may be needed by the interface

    Args:
        testbench (str): The testbench component being generated
        interface (BaseInterface): The interface currently being looked at

    Returns:
        str: Updated testbench
    """
    prologue = endpoint.prologue("")
    prologue = include.replace_variables(prologue, interface)
    testbench += prologue + "\n"
    return testbench


def add_initial_blocks(testbench, endpoint, interface):
    """
    Add any statements an interface might require within an initial block

    Args:
        testbench (str): The testbench being generated
        interface (BaseInterface): The interface currently being looked at

    Returns:
        str: Updated testbench
    """
    initial_blocks = []
    initial_blocks_raw = endpoint.initial_blocks(include.TAB_SIZE)
    for block in initial_blocks_raw:
        initial_blocks.append(include.replace_variables(block, interface))
    for block in initial_blocks:
        testbench += "initial begin\n" + block + "end\n"
    return testbench + "\n"


def instantiate_endpoint_ips(testbench, endpoint):
    """
    Instantiate any IPs required by the interfaces

    Args:
        testbench (str): The testbench being generated
        endpoint (Endpoint): The endpoint to use for adding IPs

    Returns:
        str: Updated testbench
    """
    ip_inst = endpoint.instantiate("", include.TAB_SIZE)
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


def add_interfaces(testbench_config, testbench, directory):
    """
    Add interfaces and their sources/sinks

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated
        directory (str): Path to the directory to place generated files

    Returns:
        str: The testbench
    """
    # pylint: disable=too-many-locals
    endpoints_str = ""
    imports_str = ""
    used_interfaces = {}
    leading_spaces = include.get_indentation(
        "SONAR_INCLUDE_ENDPOINTS", testbench
    )
    interfaces = testbench_config.get_from_dut("interfaces")
    # endpoints = testbench_config.get_from_dut("endpoints_flat")
    for interface_index, interface in enumerate(interfaces):
        if interface.interface_type not in used_interfaces:
            used_interfaces[interface.interface_type] = True
            imports_str += interface.core.import_packages_global()

        endpoint_str = ""
        if interface.direction == "master":
            signals = interface.core.signals["input"]
        else:
            signals = interface.core.signals["output"]
        action = {
            "signals": signals,
            "commands": [
                f"logic [$$size-1:0] $$name_$$signal_endpoint[{len(interface.endpoints)}];\n"
                f"assign $$name_$$signal = $$name_$$signal_endpoint[endpoint_select[{interface_index}]];\n"
            ],
        }
        for command in action["commands"]:
            endpoint_str = include.replace_signals(
                interface,
                action,
                command,
                endpoint_str,
                "",
                interface.core.args["sv"],
            )
        for endpoint_index, endpoint in enumerate(interface.endpoints):
            endpoint_str = add_prologue(endpoint_str, endpoint, interface)
            endpoint_str = add_initial_blocks(
                endpoint_str, endpoint, interface
            )
            endpoint_str = instantiate_endpoint_ips(endpoint_str, endpoint)

            for key in endpoint.actions["sv"].keys():
                # for key, _commands in endpoint.core.actions["sv"].items():
                endpoint_str += f"task $$interfaceType_$$index_{key}_$$endpointIndex(input logic [MAX_DATA_SIZE-1:0] args [MAX_ARG_NUM], output int retval);\n"
                endpoint_str += include.TAB_SIZE + "retval = 0;\n"
                endpoint_str = include.command_var_replace(
                    endpoint_str,
                    interface,
                    include.TAB_SIZE,
                    "sv",
                    key,
                    endpoint,
                )
                endpoint_str += "endtask\n"

            endpoint_str = endpoint_str.replace(
                "$$endpointIndex", str(endpoint_index)
            )
            endpoint.source_tcl(interface, directory)
            for key, value in endpoint.arguments.items():
                endpoint_str = endpoint_str.replace(f"$${key}", str(value))

        endpoint_str += "task $$interfaceType_$$index(input logic [MAX_DATA_SIZE-1:0] args [MAX_ARG_NUM], output int retval);\n"
        endpoint_str += include.TAB_SIZE + "retval = 0;\n"
        # for key, _commands in endpoint.core.actions["sv"].items():
        for endpoint_index, endpoint in enumerate(interface.endpoints):
            imports_str += endpoint.import_packages_local(interface)
            for key in endpoint.actions["sv"].keys():
                endpoint_str += include.TAB_SIZE
                if endpoint_index != 0:
                    endpoint_str += "else "
                arg_index = get_nth_index(endpoint.actions["sv"], key)
                endpoint_str += f"if (endpoint_select[{interface_index}] == {endpoint_index} && args[0] == {arg_index}) begin\n"
                endpoint_str += (
                    include.TAB_SIZE * 2
                    + f"$$interfaceType_$$index_{key}_$$endpointIndex(args, retval);\n"
                )
                endpoint_str += include.TAB_SIZE + "end\n"
            endpoint_str = endpoint_str.replace(
                "$$endpointIndex", str(endpoint_index)
            )

        endpoint_str += "endtask\n"
        endpoint_str = include.replace_variables(endpoint_str, interface)

        filename = interface.interface_type + f"_{interface.index}.sv"
        filepath = os.path.join(directory, filename)
        with open(filepath, "w+") as f:
            f.write(endpoint_str)
        if endpoints_str != "":
            endpoints_str += leading_spaces
        endpoints_str += f'`include "{filename}"\n'

    testbench = include.replace_in_testbenches(
        testbench, "SONAR_INCLUDE_ENDPOINTS", endpoints_str
    )
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_IMPORT_PACKAGES", imports_str[:-1]
    )
    return testbench
