"""
Defines prologue and epilogue functions for all language backends
"""

import sonar.core.backends.include as include


def add_headers(testbench_config, testbench, lang):
    """
    Add any header files to the testbench

    Args:
        testbench_config (Testbench): The testbench configuration
        testbench (str): The testbench being generated
        lang (str): Language of the testbench

    Returns:
        str: Updated testbench
    """
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
            elif header_mode == "sv":
                headers += f'`include "{header_file}"\n'
            elif header_mode == "auto":
                if header_file.endswith((".h", ".hpp")) and lang == "cpp":
                    headers += f'#include "{header_file}"\n'
                elif header_file.endswith((".v", ".sv")) and lang == "sv":
                    headers += f'`include "{header_file}"\n'
    testbench = include.replace_in_testbenches(
        testbench, "SONAR_HEADER_FILE", headers
    )
    return testbench


def prologue(testbench_config, testbench, lang):
    """
    Run prior to any language-specific backend

    Args:
        testbench_config (Testbench): Testbench configuration
        testbench (str): Testbench to generate
        lang (str): Language of the testbench

    Returns:
        str: Updated testbench
    """
    testbench = add_headers(testbench_config, testbench, lang)

    return testbench
