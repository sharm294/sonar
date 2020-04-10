import pytest
from pathlib import Path
from unittest.mock import patch
import os
import sys

import sonar.main
from sonar.include import Constants, init_constants


@pytest.fixture(scope="session")
def test_home(tmpdir_factory):
    fn = tmpdir_factory.mktemp("home")
    return fn


@pytest.fixture(scope="session", autouse=True)
def test_dir(tmpdir_factory):
    base_path = Path(tmpdir_factory.getbasetemp())

    class TestPaths:
        class VivadoPaths:
            non_existent = base_path.joinpath("DOES_NOT_EXIST")
            no_vivado = base_path.joinpath("Xilinx")
            one_vivado = base_path.joinpath("Xilinx/Xilinx_1")
            many_vivado = base_path.joinpath("Xilinx/Xilinx_2")

        class RepoPaths:
            repo_base_path = base_path.joinpath("repos")
            valid = repo_base_path.joinpath("valid")

        vivado = VivadoPaths()
        repos = RepoPaths()

    one_vivado = TestPaths.vivado.one_vivado.joinpath("Vivado/2017.2")
    two_vivado_0 = TestPaths.vivado.many_vivado.joinpath("Vivado/2017.3")
    two_vivado_1 = TestPaths.vivado.many_vivado.joinpath("Vivado/2018.2")

    one_vivado.mkdir(parents=True)
    two_vivado_0.mkdir(parents=True)
    two_vivado_1.mkdir(parents=True)

    TestPaths.repos.valid.mkdir(parents=True)

    return TestPaths


@pytest.fixture(autouse=True)
def patch_constants(monkeypatch, test_home):
    @init_constants
    class MockConstants(Constants):
        SONAR_BASE_PATH = Path(test_home)

    monkeypatch.setattr("sonar.api.Constants", MockConstants)
    monkeypatch.setattr("sonar.database.Constants", MockConstants)
    monkeypatch.setattr("sonar.include.Constants", MockConstants)


class CallSonar:
    @staticmethod
    def cli(args=""):
        testargs = ["sonar"]
        testargs.extend(args.split(" "))
        with pytest.raises(SystemExit) as exc:
            with patch.object(sys, "argv", testargs):
                sonar.main.main()
        return exc.value.code

    def abs_path():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def call_sonar():
    return CallSonar


class Helper:
    @staticmethod
    def check_filesystem(base_path, directories=None, files=None, check_all=True):
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
            for dirpath, f_directories, f_files in os.walk(base_path):
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
    return Helper
