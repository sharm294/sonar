"""
Configure pytest for sonar
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import sonar.main
from sonar.core.include import Constants, init_constants


@pytest.fixture(scope="session")
def test_home_path(tmpdir_factory):
    """
    Makes a home directory for testing

    Args:
        tmpdir_factory (tmpdir_factory): Defined in pytest to make a temporary
            directory

    Returns:
        str: The path to the directory
    """
    home_path = tmpdir_factory.mktemp("home")
    return home_path


@pytest.fixture(scope="session", autouse=True)
def test_dir(tmpdir_factory):
    """
    Creates the directory structure in the temporary test directory for the
    various tests

    Args:
        tmpdir_factory (tmpdir_factory): Defined in pytest to make a temporary
            directory

    Returns:
        object: Holds the various paths created as object attributes
    """
    base_path = Path(tmpdir_factory.getbasetemp())

    class TestPaths:
        """
        Holds the paths created as attributes
        """

        class VivadoPaths:
            """
            Vivado paths are used to test the vivado initialization function
            """

            non_existent = base_path.joinpath("DOES_NOT_EXIST")
            no_vivado = base_path.joinpath("Xilinx")
            one_vivado = base_path.joinpath("Xilinx/Xilinx_1")
            many_vivado = base_path.joinpath("Xilinx/Xilinx_2")

        class RepoPaths:
            """
            Used to test creating repositories
            """

            repo_base_path = base_path.joinpath("repos")
            valid = repo_base_path.joinpath("valid")

        class Testbench:
            """
            Testbench tests
            """

            testbench = base_path.joinpath("testbench")
            hello_world = testbench.joinpath("hello_world")

        class Shell:
            """
            Shell tests
            """

            shell = base_path.joinpath("shell")
            hello_world = shell.joinpath("hello_world")

        vivado = VivadoPaths()
        repos = RepoPaths()
        testbench = Testbench()
        shell = Shell()
        base = base_path

    one_vivado = TestPaths.vivado.one_vivado.joinpath("Vivado/2017.2")
    two_vivado_0 = TestPaths.vivado.many_vivado.joinpath("Vivado/2017.3")
    two_vivado_1 = TestPaths.vivado.many_vivado.joinpath("Vivado/2018.2")

    one_vivado.mkdir(parents=True)
    two_vivado_0.mkdir(parents=True)
    two_vivado_1.mkdir(parents=True)

    TestPaths.repos.valid.mkdir(parents=True)

    TestPaths.testbench.hello_world.mkdir(parents=True)

    TestPaths.shell.hello_world.mkdir(parents=True)

    return TestPaths


@pytest.fixture(autouse=True)
def patch_constants(
    monkeypatch, test_home_path
):  # pylint: disable=redefined-outer-name
    """
    For pytest, override the default constants used in sonar

    Args:
        monkeypatch (monkeypatch): Defined in pytest for monkeypatching code
        test_home_path (str): Path to the new home directory for sonar
    """

    @init_constants
    class MockConstants(Constants):
        """
        New mock Constants class that inherits all the constants from the base
        class but overrides the base path to our temporary home path
        """

        SONAR_BASE_PATH = Path(test_home_path)

    # each of these files imports their own version of the Constants so we need
    # to override all of them. Within the test directory, we use the full import
    # path to import constants to avoid this requirement.
    monkeypatch.setattr("sonar.api.Constants", MockConstants)
    monkeypatch.setattr("sonar.database.Constants", MockConstants)
    monkeypatch.setattr("sonar.core.include.Constants", MockConstants)


class CallSonar:
    """
    Allows pytest tests to call sonar
    """

    @staticmethod
    def cli(args=""):
        """
        Calls sonar from Python as though it were called from the command line

        Args:
            args (str, optional): Arguments to pass to sonar. Defaults to "".

        Returns:
            int: Return value from calling sonar
        """
        testargs = ["sonar"]
        testargs.extend(args.split(" "))
        with pytest.raises(SystemExit) as exc:
            with patch.object(sys, "argv", testargs):
                sonar.main.main()
        return exc.value.code

    @staticmethod
    def abs_path():
        """
        Get the absolute path to the sonar repository

        Returns:
            str: Path to the sonar repository
        """
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def call_sonar():
    """
    Pytest fixture that just fetches the CallSonar object

    Returns:
        CallSonar: Allows pytest tests to call sonar
    """
    return CallSonar


class Helper:
    """
    Helpful functions for pytest tests
    """

    @staticmethod
    def check_filesystem(
        base_path, directories=None, files=None, check_all=True
    ):
        """
        Check the filesystem at a given path to make sure that the listed files
        and/or directories all exist

        Args:
            base_path (str): The base path to search from
            directories (list, optional): List of directories to search.
                Defaults to None.
            files (list, optional): List of files to search. Defaults to None.
            check_all (bool, optional): Check if there are extra files/directories
                from the ones listed. Defaults to True.

        Returns:
            Tuple: (list of missing files/dirs, list of extra files/dirs)
        """
        # pylint: disable=too-many-branches
        assert (
            directories is not None or files is not None
        ), "One of directories or files must be specified"

        assert (
            isinstance(files, list) or files is None
        ), "Argument must be list of files to search for"
        assert (
            isinstance(directories, list) or directories is None
        ), "Argument must be list of directories to search for"

        missing_files = []
        extra_files = []

        if files is not None:
            full_files = []
            for filename in files:
                filepath = os.path.join(base_path, filename)
                full_files.append(filepath)
                if not os.path.exists(filepath):
                    missing_files.append(filename)

        if directories is not None:
            full_directories = []
            for dirname in directories:
                dirpath = os.path.join(base_path, dirname)
                full_directories.append(dirpath)
                if not os.path.exists(dirpath):
                    missing_files.append(dirname)

        if check_all:
            for dirpath, _, f_files in os.walk(base_path):
                if directories is not None:
                    if dirpath not in full_directories:
                        if dirpath != base_path:
                            extra_files.append(dirpath)
                if files is not None:
                    for f in f_files:
                        filepath = os.path.join(dirpath, f)
                        if filepath not in full_files:
                            extra_files.append(filepath)

        return missing_files, extra_files


@pytest.fixture
def helper():
    """
    Pytest fixture that just fetches the Helper object

    Returns:
        Helper: Helpful functions for pytest tests
    """
    return Helper
