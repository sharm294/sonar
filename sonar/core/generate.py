"""
Generate the testbenches based on the configuration defined by the user.
"""

import logging
import os

from sonar.core.backends.common import prologue
from sonar.core.backends.cpp import create_testbench as create_cpp_testbench
from sonar.core.backends.sv import create_testbench as create_sv_testbench
from sonar.exceptions import SonarInvalidArgError

logger = logging.getLogger(__file__)


def filter_langs(active_langs, sonar_tb_filepath):
    """
    If any of the generated testbenches are newer than the sonar testbench
    script, skip generating it. This probably implies the user has manually
    edited the generated testbench.

    Args:
        active_langs (tuple): Original list of languages to use

    Returns:
        tuple: Filtered list of languages to generate testbenches for
    """
    try:
        sonar_tb_file_time = os.path.getmtime(sonar_tb_filepath)
    except FileNotFoundError:
        # in this case, the testbench is being generated not relative to the
        # source sonar testbench file or there's a typo. Log it and move on
        logger.warning(
            "File %s not found, so not filtering languages by creation time",
            sonar_tb_filepath,
        )
        return active_langs
    active_langs_tmp = []
    for lang in active_langs:
        if os.path.exists(get_tb_filepath(sonar_tb_filepath, lang)):
            tb_time = os.path.getmtime(
                get_tb_filepath(sonar_tb_filepath, lang)
            )
            if tb_time <= sonar_tb_file_time:
                active_langs_tmp.append(lang)
        else:
            active_langs_tmp.append(lang)
    return active_langs_tmp


def parse_sonar_tb(sonar_tb_filepath):
    """
    From the passed in sonar_tb_filepath, extract the name of the file and
    the directory relative to which the generated files will be created

    Args:
        sonar_tb_filepath (str): Path to the file used to create the
            testbench_config

    Returns:
        tuple: The name of the DUT, directory in which to place generated files
    """
    dut_name = os.path.basename(sonar_tb_filepath)[:-3]
    directory = os.path.join(
        os.path.dirname(sonar_tb_filepath), "build", dut_name
    )
    return dut_name, directory


def get_tb_filepath(sonar_tb_filepath, lang):
    """
    Get the path of the generated testbench for a particular language

    Args:
        sonar_tb_filepath (str): Path to the file used to create the
            testbench_config
        lang (str): Language of the testbench

    Returns:
        str: Path to the testbench file
    """
    dut_name, directory = parse_sonar_tb(sonar_tb_filepath)
    return os.path.join(directory, dut_name + f"_tb.{lang}")


def get_data_filepath(sonar_tb_filepath, lang):
    """
    Get the path of the generated data file for a particular language

    Args:
        sonar_tb_filepath (str): Path to the file used to create the
            testbench_config
        lang (str): Language of the testbench

    Returns:
        str: Path to the data file
    """
    dut_name, directory = parse_sonar_tb(sonar_tb_filepath)
    return os.path.join(directory, dut_name + f"_{lang}.dat")


def finalize_waits(testbench_config):
    """
    Using the test vectors in the testbench, this method aggregates all the
    wait conditions as required for the Sonar backend

    Args:
        testbench_config (Testbench): The user-defined testbench configuration

    Returns:
        Testbench: Updated testbench configuration
    """

    def update_waits(index, temp_key):
        if temp_key.isdigit():
            if int(temp_key) >= index:
                raise Exception
            return None, index
        if temp_key not in conditions:
            new_key = str(index)
            waits.append({"condition": temp_key, "key": new_key})
            conditions.append(temp_key)
            index += 1
            return new_key, index
        for wait in waits:
            if wait["condition"] == temp_key:
                key = wait["key"]
                break
        return key, index

    waits = []
    conditions = []
    flag_present = False
    index = 0
    for vector in testbench_config.vectors:
        for thread in vector.threads:
            for command in thread.commands:
                if "wait" in command:
                    temp_key = command["wait"]["key"]
                    if temp_key == "flag":
                        flag_present = True
                        continue
                    updated_key, index = update_waits(index, temp_key)
                    if updated_key:
                        command["wait"]["key"] = updated_key
    if flag_present:
        waits.append({"condition": "wait(flags[args[0]]);", "key": "flag"})
    testbench_config.wait_conditions = waits
    return testbench_config


def configure_prologue(testbench_config):
    """
    If a prologue thread is added, add it to all test vectors and delay other
    threads to wait for it to finish

    Args:
        testbench_config (Testbench): The user-defined testbench configuration

    Returns:
        Testbench: Updated testbench configuration
    """
    if testbench_config.prologue_thread is None:
        return testbench_config
    prologue_thread = testbench_config.prologue_thread
    prologue_thread.commands.insert(
        0, {"signal": {"name": "test_prologue", "value": 1}}
    )
    prologue_thread.set_signal("test_prologue", 0)
    for vector in testbench_config.vectors:
        for thread in vector.threads:
            thread.commands.insert(
                0, {"wait": {"key": "@(negedge test_prologue);"}}
            )
        vector.add_thread(prologue_thread)
    return testbench_config


def legalize_config(testbench_config):
    """
    There are some additional automatic steps that must be performed on the
    testbench configuration once the user has finished it

    Args:
        testbench_config (Testbench): The user-defined testbench configuration

    Returns:
        Testbench: Updated testbench configuration
    """
    testbench_config = configure_prologue(testbench_config)
    testbench_config = finalize_waits(testbench_config)
    return testbench_config


# TODO error handling
# TODO make seek size programmatic
# TODO allow delays by clock cycles
def sonar(
    testbench_config,
    sonar_tb_filepath,
    languages="sv",
    force=False,
    legalize=True,
):
    """
    Call the appropriate backends to generate testbenches in the chosen
    languages.

    Args:
        testbench_config (Testbench): The user-defined testbench configuration
        sonar_tb_filepath (str): Path to the Python file used to generate
            testbench_config
        languages (str or tuple, optional): Language(s) to generate testbenches
            for. Defaults to "sv".
        force (bool, optional): Force testbench generation. Defaults to False
        legalize (bool, optional): Perform testbench legalization on the config

    Raises:
        SonarInvalidArgError: Raised for invalid languages
    """
    if legalize:
        testbench_config = legalize_config(testbench_config)
        print(testbench_config)

    if isinstance(languages, str):
        if languages == "all":
            active_langs = ("sv", "cpp")
        else:
            active_langs = (languages,)
    elif isinstance(languages, (list, tuple)):
        active_langs = tuple(languages)
    else:
        raise SonarInvalidArgError(
            "Languages must be specified as a string or an iterable"
        )

    _, directory = parse_sonar_tb(sonar_tb_filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not force:
        active_langs = filter_langs(active_langs, sonar_tb_filepath)

    testbenches = {}
    data_files = {}
    for lang in active_langs:
        template = os.path.join(
            os.path.dirname(__file__), "templates", f"template_tb.{lang}"
        )
        with open(template, "r") as f:
            testbenches[lang] = f.read()
        testbenches[lang] = prologue(testbench_config, testbenches[lang], lang)

    if "sv" in active_langs:
        testbenches["sv"], data_files["sv"] = create_sv_testbench(
            testbench_config, testbenches["sv"], directory
        )
    if "cpp" in active_langs:
        testbenches["cpp"], data_files["cpp"] = create_cpp_testbench(
            testbench_config, testbenches["cpp"], directory
        )

    for lang in active_langs:
        with open(get_tb_filepath(sonar_tb_filepath, lang), "w+") as f:
            f.write(testbenches[lang])
        with open(get_data_filepath(sonar_tb_filepath, lang), "w+") as f:
            f.write(data_files[lang])
