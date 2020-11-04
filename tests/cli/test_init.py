"""
Tests the initialization methods
"""

import pytest

import sonar.database as Database
from sonar.exceptions import ReturnValue


class TestVivado:
    """
    Group the Vivado initializations
    """

    @pytest.fixture(autouse=True)
    def setup(self, test_dir, call_sonar):
        """
        Add shared objects from pytest for all tests to use

        Args:
            test_dir (TestPaths): Used to hold test directories
            call_sonar (CallSonar): Used to call sonar from Python
        """
        # pylint: disable=attribute-defined-outside-init
        self.paths = test_dir.vivado
        self.sonar = call_sonar.cli

    def test_vivado_fake_path(self):
        """
        Attempts to initialize from a non-existent path
        """
        exit_code = self.sonar("init vivado " + str(self.paths.non_existent))
        assert exit_code == ReturnValue.SONAR_NONEXISTENT_PATH

    def test_vivado_no_vivado(self):
        """
        Attempts to initialize from a path where no Vivado installations exist
        """
        exit_code = self.sonar("init vivado " + str(self.paths.no_vivado))
        assert exit_code == ReturnValue.SONAR_INVALID_PATH

    def test_vivado_one_vivado(self):
        """
        Initialize from a directory containing one Vivado installation
        """
        exit_code = self.sonar("init vivado " + str(self.paths.one_vivado))
        assert exit_code == ReturnValue.SONAR_OK
        env = Database.Env.get()
        assert "vivado_2017.2" in env

    def test_vivado_many_vivado(self):
        """
        Initialize from a directory containing multiple Vivado installations
        """
        exit_code = self.sonar("init vivado " + str(self.paths.many_vivado))
        assert exit_code == ReturnValue.SONAR_OK
        env = Database.Env.get()
        assert "vivado_2017.3" in env
        assert "vivado_2018.2" in env
