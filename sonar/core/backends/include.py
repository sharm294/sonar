"""
Defines some shared functions for all language backends to use
"""

from __future__ import annotations

import copy
import re
from typing import TYPE_CHECKING, Any, Type, Union

import sonar.interfaces.axi4_lite_slave
import sonar.interfaces.axi4_stream

if TYPE_CHECKING:
    import sonar.interfaces.base_interface as base_interface


def get_indentation(keyword, search_str):
    """
    In a multi-line string with new line characters, find the indentation of a
    search string. Currently assumes that spaces are used for indentation and
    the search string directly follows the indent.

    Args:
        keyword (string): The keyword to search for
        search_str (string): String to search

    Returns:
        string: The indent
    """
    regex_variable = re.compile(r"\n( *)" + keyword)
    match = re.search(regex_variable, search_str)
    if match:
        return match.group(1)
    return ""


def replace_in_testbenches(
    testbenches, search_str, replace, include_langs=None, exclude_langs=None
):
    """
    In a testbench, replace a string with another string.

    Args:
        testbenches (str or dict): The testbench to replace text in. This may be
            a string representing a single testbench or a dictionary where
            different testbenches are indexed by language
        search_str (str): String to search for
        replace (str-like): Converted to string and used to replace search_str
        include_langs (iterable, optional): Iterable of a subset of languages to
            perform the replacement. Defaults to None.
        exclude_langs (iterable, optional): Iterable of a subset of languages to
            exclude from replacement. Defaults to None.

    Returns:
        str or dict: The modified testbench. Same type as testbenches
    """
    if isinstance(testbenches, str):
        testbenches = testbenches.replace(search_str, str(replace))
    else:
        for lang in [*testbenches]:
            if include_langs and lang not in include_langs:
                continue
            if exclude_langs and lang in exclude_langs:
                continue

            if isinstance(replace, dict):
                if lang in replace:
                    replace_str = str(replace[lang]).replace("$$lang", lang)
                else:
                    replace_str = ""
            else:
                replace_str = str(replace).replace("$$lang", lang)
            testbenches[lang] = testbenches[lang].replace(
                search_str, replace_str
            )
    return testbenches


def get_data_file_args(args, language):
    """
    For a interface, return the language-specific set of data file arguments

    Args:
        args (dict): Dictionary of data file arguments for an interface
        language (str): Language of the testbench

    Returns:
        dict: Language-specific data file arguments
    """
    if language in args:
        return args[language]
    return args["generic"]


def replace_variables(
    input_string: str, interface: Any, key: Union[int, None] = None
) -> str:
    """
    In a string, replace all the "$$X" variables with their definitions from the
    interface.

    Args:
        input_string (str): String containing $$X variables
        interface (Any): An interface
        key (Union[int, None], optional): If the replacement string is a data
            structure, use this key to index it. Defaults to None.

    Returns:
        str: Updated string
    """

    regex_variable = re.compile(r"\$\$[^_|\W]+")
    for variable in re.findall(regex_variable, input_string):
        new_variable = getattr(interface, variable[2:])
        if isinstance(new_variable, (list, tuple)):
            if key is None:
                raise ValueError
            new_variable = new_variable[key]
        input_string = input_string.replace(variable, str(new_variable))
    return input_string


def replace_block(target_string, command, interface, indent, key=None):
    """
    For multi-line code blocks, replace the $$X variables in it while respecting
    indentation

    Args:
        target_string (str): The preceding string to append this block onto
        command (str): The block in which to replace things
        interface (???): An interface
        indent (str): String to add as leading indent for each line
        key (str or int, optional): If the replacement string is a data
            structure, use this key to index it. Defaults to None.

    Returns:
        str: The updated target_string
    """
    # command = command.replace("$$name", interface.name)
    command = replace_variables(command, interface, key)
    command = command.replace("\n", "\n" + indent)
    target_string += indent + command + "\n"
    return target_string


def replace_signals(interface, action, command, target_string, indent, args):
    """
    This function performs duplication and text replacement for $$signals

    Args:
        interface (???): An interface
        action (dict):
        command (str): The string in which to replace signals
        target_string (str): The preceding string to append this block to
        indent (str): String to add as leading indent for each line
        args (dict): The order of interface arguments as a function of language

    Returns:
        str: The updated target_string
    """
    for signal_type, _ in interface.signals.items():
        if signal_type in action["signals"]:
            command_copy = copy.deepcopy(command)
            command_copy = command_copy.replace("$$signal", signal_type)
            idx = str(args[signal_type])
            command_copy = command_copy.replace("$$i", idx)
            target_string = replace_block(
                target_string, command_copy, interface, indent
            )
    return target_string


def command_var_replace(
    target_string, interface, indent, language, action_type
):
    """
    This function replaces the variables in an interface action block. There
    are two named variables: $$name (referring to the interface name) and
    $$signal (referring to a particular side signal). All other $$ variables
    must be keys in the interface declaration in the configuration file.

    Args:
        target_string (str): The preceding string to append to
        interface (???): An interface
        indent (str): String to add as leading indent for each line
        language (str): Language of the testbench
        action_type (str): Identifier for the list of actions to perform

    Returns:
        str: The updated target_string
    """
    actions = interface.core.actions[language][action_type]
    for action in actions:
        # check if there is a command to repeat for a set of signals
        if isinstance(action, dict):
            if "signals" in action:
                for command in action["commands"]:
                    regex_signal = re.compile(r"\$\$signal")
                    if re.findall(
                        regex_signal, command
                    ):  # if $$signal in command
                        target_string = replace_signals(
                            interface,
                            action,
                            command,
                            target_string,
                            indent,
                            interface.core.args[language],
                        )
                    else:
                        command_copy = copy.deepcopy(command)
                        target_string = replace_block(
                            target_string, command_copy, interface, indent
                        )
            else:
                for index, _entity in enumerate(
                    getattr(interface, action["foreach"])
                ):
                    for command in action["commands"]:
                        command_copy = copy.deepcopy(command)
                        target_string = replace_block(
                            target_string,
                            command_copy,
                            interface,
                            indent,
                            index,
                        )
        else:
            command_copy = copy.deepcopy(action)
            target_string = replace_block(
                target_string, command_copy, interface, indent
            )

    return target_string


def set_metadata(testbench_config, testbench):
    """
    Perform the direct substitutions from the sonar testbench metadata into the
    the testbench

    Args:
        testbench_config (Testbench): Sonar testbench description
        testbench (str): The testbench template
    """
    for key, value in testbench_config.metadata.items():
        if value is None:
            replace_str = ""
        else:
            replace_str = str(value)
        search_str = "SONAR_" + key.upper()
        testbench = replace_in_testbenches(testbench, search_str, replace_str)
    return testbench


def get_interface(interface_name: str) -> Type[base_interface.InterfaceCore]:
    """
    Import an interface from sonar

    Args:
        interface_name (str): Name of the interface

    Returns:
        Type[base_interface.InterfaceCore]: The interface
    """
    if interface_name == "axi4_stream":
        return sonar.interfaces.axi4_stream.AXI4StreamCore
    if interface_name == "axi4_lite_slave":
        return sonar.interfaces.axi4_lite_slave.AXI4LiteSlaveCore
    print(interface_name)
    raise ValueError
