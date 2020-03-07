import os
import pytest

from sonar.exceptions import ReturnValue
from sonar.include import Constants


class TestProject:
    @pytest.fixture(autouse=True)
    def setup(self, test_dir, call_sonar):
        self.paths = test_dir.repos
        self.sonar = call_sonar.cli

    def test_add_no_arg(self):
        exit_code = self.sonar("project add")
        assert exit_code == Constants.ARGPARSE_FAILURE

    def test_add(self):
        os.chdir(self.paths.valid)
        exit_code = self.sonar("project add ip_0")
        ip_path = self.paths.valid.joinpath("ip_0")
        assert os.path.exists(ip_path.joinpath("build/bin"))
        assert os.path.exists(ip_path.joinpath("cad"))
        assert os.path.exists(ip_path.joinpath("hls"))
        assert os.path.exists(ip_path.joinpath("src"))
        assert os.path.exists(ip_path.joinpath("include"))
        assert exit_code == ReturnValue.SONAR_OK
