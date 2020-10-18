import os
import pytest
import toml

from sonar.exceptions import ReturnValue
from sonar.core.include import Constants


class TestCreate:
    @pytest.fixture(autouse=True)
    def setup(self, test_dir, call_sonar):
        self.paths = test_dir.repos
        self.sonar = call_sonar.cli

    def test_create_ip_no_arg(self):
        exit_code = self.sonar("create ip")
        assert exit_code == Constants.ARGPARSE_FAILURE

    def test_create_repo(self, helper, monkeypatch):
        os.chdir(self.paths.valid)
        exit_code = self.sonar("create repo test_repo")
        repo_path = self.paths.valid.joinpath("test_repo")
        missing_files, extra_files = helper.check_filesystem(
            str(repo_path),
            [".sonar"],
            [".sonar/gitlint_rules.py", Constants.SONAR_CONFIG_FILE_PATH, ".gitignore"],
        )
        assert not missing_files
        assert not extra_files

        init = toml.load(repo_path.joinpath(Constants.SONAR_CONFIG_FILE_PATH))
        assert init["project"]["name"] == "test_repo"
        assert exit_code == ReturnValue.SONAR_OK

        def test_create_ip(monkeypatch):
            self.sonar("repo activate test_repo")
            monkeypatch.setenv("SONAR_REPO", str(repo_path))
            os.chdir(repo_path)
            exit_code = self.sonar("create ip ip_0")
            ip_path = repo_path.joinpath("ip_0")
            missing_files, extra_files = helper.check_filesystem(
                str(ip_path),
                ["build", "build/bin", "cad", "hls", "src", "include", "testbench", "testbench/build", "testbench/build/bin"],
            )
            assert not missing_files
            assert not extra_files
            assert exit_code == ReturnValue.SONAR_OK

        test_create_ip(monkeypatch)
