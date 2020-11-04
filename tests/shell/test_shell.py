"""
Python wrapper for calling shell-based end-to-end tests
"""

import os
import shutil
import subprocess


def test_shell_hello_world(test_dir, call_sonar):
    """
    Test the hello_world example

    Args:
        test_dir (TestPaths): Used to hold test directories
        call_sonar (CallSonar): Used to call sonar from Python
    """
    run_script = os.path.join(call_sonar.abs_path(), "tests/shell/test.sh")
    test_script = os.path.join(
        call_sonar.abs_path(), "tests/shell/test_hello_world.sh"
    )
    this_test_dir = str(test_dir.shell.hello_world)

    base_path = os.path.join(
        call_sonar.abs_path(), "examples/projects/hello_world"
    )
    files_to_copy = [
        os.path.join(base_path, "hello_world.cpp"),
        os.path.join(base_path, "hello_world.hpp"),
        os.path.join(base_path, "hello_world.py"),
    ]
    for each_file in files_to_copy:
        shutil.copy(each_file, this_test_dir)

    subprocess.run([run_script, test_script, this_test_dir], check=True)
