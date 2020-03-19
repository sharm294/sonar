import pytest
from pathlib import Path
from unittest.mock import patch
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


@pytest.fixture
def call_sonar():
    return CallSonar
