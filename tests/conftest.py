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


@pytest.fixture(autouse=True)
def patch_constants(monkeypatch, test_home):
    @init_constants
    class MockConstants(Constants):
        SONAR_BASE_PATH = Path(test_home)

    monkeypatch.setattr("sonar.cli.Constants", MockConstants)
    monkeypatch.setattr("sonar.main.Constants", MockConstants)
    monkeypatch.setattr("sonar.include.Constants", MockConstants)


class CallSonar:
    @staticmethod
    def cli(*args):
        testargs = ["sonar"]
        testargs.extend(args)
        with pytest.raises(SystemExit) as exc:
            with patch.object(sys, "argv", testargs):
                sonar.main.main()
        return exc.value.code


@pytest.fixture
def call_sonar():
    return CallSonar
