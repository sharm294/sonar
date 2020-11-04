"""
Test creating repositories and IPs
"""

import os

import pytest
import toml

from sonar.core.include import Constants
from sonar.exceptions import ReturnValue


class TestCreate:
    """
    Group the creation tests
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
        self.paths = test_dir.repos
        self.sonar = call_sonar.cli

    def test_create_ip_no_arg(self):
        """
        Attempt to create an IP with no arguments
        """
        exit_code = self.sonar("create ip")
        assert exit_code == Constants.ARGPARSE_FAILURE

    def test_create_repo(self, helper, monkeypatch):
        """
        Create a repository

        Args:
            helper (Helper): Used to hold shared functions for tests to use
            monkeypatch (MonkeyPatch): Defined in pytest for monkeypatching code
        """
        os.chdir(self.paths.valid)
        exit_code = self.sonar("create repo test_repo")
        repo_path = self.paths.valid.joinpath("test_repo")
        missing_files, extra_files = helper.check_filesystem(
            str(repo_path),
            [".sonar"],
            [
                ".sonar/gitlint_rules.py",
                Constants.SONAR_CONFIG_FILE_PATH,
                ".gitignore",
            ],
        )
        assert not missing_files
        assert not extra_files

        init = toml.load(repo_path.joinpath(Constants.SONAR_CONFIG_FILE_PATH))
        assert init["project"]["name"] == "test_repo"
        assert exit_code == ReturnValue.SONAR_OK

        def test_create_ip(monkeypatch):
            """
            In a created repository, create a new IP

            Args:
                monkeypatch (MonkeyPatch): Defined in pytest for monkeypatching code
            """
            self.sonar("repo activate test_repo")
            monkeypatch.setenv("SONAR_REPO", str(repo_path))
            os.chdir(repo_path)
            exit_code = self.sonar("create ip ip_0")
            ip_path = repo_path.joinpath("ip_0")
            missing_files, extra_files = helper.check_filesystem(
                str(ip_path),
                [
                    "build",
                    "build/bin",
                    "cad",
                    "hls",
                    "src",
                    "include",
                    "testbench",
                    "testbench/build",
                    "testbench/build/bin",
                ],
            )
            assert not missing_files
            assert not extra_files
            assert exit_code == ReturnValue.SONAR_OK

        test_create_ip(monkeypatch)
