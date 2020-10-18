import copy
import re
import importlib

def get_indentation(keyword, search_str):
    regex_variable = re.compile(r"\n( *)" + keyword)
    match = re.search(regex_variable, search_str)
    if match:
        return match.group(1)
    return ""

def replace_in_testbenches(testbenches, search_str, replace, include_langs=None, exclude_langs=None):
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
            testbenches[lang] = testbenches[lang].replace(search_str, replace_str)
    return testbenches

def get_from_dut(testbench_config, key):
    dut = testbench_config.modules["DUT"]
    if key == "interfaces":
        return dut.ports.get_interfaces()
    if key == "interfaces_dict":
        return dut.ports.get_interfaces(collapse=False)
    if key == "signals":
        return dut.ports.get_signals()
    if key == "wait_conditions":
        return testbench_config.wait_conditions
    return getattr(dut, key)

################################################################################
### channelToIndex ###
# This function finds the index of a particular channel based on its name
def channelToIndex(channelType, args):
    for idx, channel in enumerate(args):
        if channel == channelType:
            return idx

    return None

################################################################################
### replaceVar ###
# This function relaces all $$X variables using the interface as the source
def replaceVar(inputStr, interface, key=None):
    regex_variable = re.compile(r"\$\$[^_|\W]+")
    for variable in re.findall(regex_variable, inputStr):
        new_variable = getattr(interface, variable[2:])
        if isinstance(new_variable, (list, dict, tuple)):
            new_variable = new_variable[key]
        inputStr = inputStr.replace(variable, str(new_variable))
    return inputStr


################################################################################
### commandVarReplaceSub ###
# This function replaces any $variables with their corresponding key from the
# YAML
def commandVarReplaceSub(elseif_interfaceIn, command, interface, indent, key=None):
    command = command.replace("$$name", interface.name)
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
    for channel in interface.channels:
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
def command_var_replace(elseif_interfaceIn, interface, actions, indent, args):
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
                for index, _entity in enumerate(getattr(interface, action["foreach"])):
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

# This function attempts to import an interface definition
def get_interface(interfaceName):
    # first check user's directory
    # try:
    #     interface = importlib.import_module("user.interfaces." + interfaceName)
    # except ImportError:
    #     pass
    # else:
    #     return interface

    # then check Sonar directory
    interface = importlib.import_module(
        "sonar.core.interfaces." + interfaceName
    )
    return interface
