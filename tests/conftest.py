import pytest
from pathlib import Path
from unittest.mock import patch
import sys

import sonar
from sonar.include import Constants, init_constants


@pytest.fixture(scope="session")
def test_home(tmpdir_factory):
    fn = tmpdir_factory.mktemp("home")
    return fn


@pytest.fixture(scope="session")
def test_vivado_path(tmpdir_factory):
    base_path = Path(tmpdir_factory.getbasetemp())

    class VivadoPath:
        non_existent = base_path.joinpath("DOES_NOT_EXIST")
        no_vivado = base_path.joinpath("Xilinx")
        one_vivado = base_path.joinpath("Xilinx/Xilinx_1")
        many_vivado = base_path.joinpath("Xilinx/Xilinx_2")

    one_vivado = VivadoPath.one_vivado.joinpath("Vivado/2017.2")
    two_vivado_0 = VivadoPath.many_vivado.joinpath("Vivado/2017.3")
    two_vivado_1 = VivadoPath.many_vivado.joinpath("Vivado/2018.2")

    one_vivado.mkdir(parents=True)
    two_vivado_0.mkdir(parents=True)
    two_vivado_1.mkdir(parents=True)
    # fn = tmpdir_factory.mktemp("Xilinx")

    return VivadoPath


@pytest.fixture(autouse=True)
def patch_constants(monkeypatch, test_home):
    @init_constants
    class MockConstants(Constants):
        SONAR_BASE_PATH = Path(test_home)

    monkeypatch.setattr("sonar.cli.Constants", MockConstants)
    monkeypatch.setattr("sonar.main.Constants", MockConstants)
    monkeypatch.setattr("sonar.include.Constants", MockConstants)
    monkeypatch.setattr("sonar.database.Constants", MockConstants)


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
