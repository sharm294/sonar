"""
Unit tests for the sonar database
"""

import os
import textwrap

import pytest
import toml

import sonar.api
import sonar.core.include
import sonar.database
import sonar.exceptions


def test_find_fpga_family():
    """
    Test the Xilinx FPGA part -> family mappings
    """
    fpgas = [
        ("xcku3p-ffva676-1L-i", "Kintex_Ultrascale_Plus"),
        ("xcku115-flva1517-2-e", "Kintex_Ultrascale"),
        ("xcvu3p-ffvc1517-2L-e", "Virtex_Ultrascale_Plus"),
        ("xcvu065-ffvc1517-2-e", "Virtex_Ultrascale"),
        ("xc7v2000tflg1925-1", "7series_Virtex"),
        ("zc7z007sclg400-1", "7series_Zynq"),
        ("xc7k70tfbg676-3", "7series_Kintex"),
        ("xczu2cg-sbva484-2-e", "Zynq_Ultrascale_Plus"),
    ]

    for fpga in fpgas:
        family = sonar.database.Board._find_part_family(fpga[0])
        assert family == fpga[1]


def mock_config(_path):
    """
    Load a mock config to override toml.load()

    Args:
        path (str): Normally, the path to the TOML is provided

    Returns:
        dict: The interpreted TOML file
    """
    return {"project": {"name": "valid"}}


class TestTool:
    """
    Test the tool-related parts of the database
    """

    @pytest.fixture(autouse=True)
    def setup(self):  # pylint: disable=no-self-use
        """
        Verify that the database exists
        """
        sonar.api.check_database()

    @staticmethod
    def test_get():
        """
        Test 'get' for tools
        """
        sonar.database.init()
        with pytest.raises(sonar.exceptions.SonarInvalidArgError):
            tool = sonar.database.Tool.get("quartus")

        sonar.database.Tool.add(
            "vivado",
            "2017.2",
            "vivado",
            "vivado_hls",
            "vivado",
            textwrap.dedent(
                """\
            source xzy
            export this=foo
        """
            ),
        )
        tool = sonar.database.Tool.get("vivado")
        assert tool == {
            "versions": ["2017.2"],
            "executable": {
                "cad": "vivado",
                "hls": "vivado_hls",
                "sim": "vivado",
            },
            "script": {"2017.2": "source xzy\nexport this=foo\n"},
        }

        sonar.database.Tool.add(
            "vivado",
            "2017.3",
            "vivado",
            "vivado_hls",
            "vivado",
            textwrap.dedent(
                """\
            source zyx
            export this=bar
        """
            ),
        )
        tools = sonar.database.Tool.get()
        tool = tools["vivado"]
        assert tool == {
            "versions": ["2017.2", "2017.3"],
            "executable": {
                "cad": "vivado",
                "hls": "vivado_hls",
                "sim": "vivado",
            },
            "script": {
                "2017.2": "source xzy\nexport this=foo\n",
                "2017.3": "source zyx\nexport this=bar\n",
            },
        }

    @staticmethod
    def test_activate():
        """
        Test activating a tool
        """
        sonar.database.init()
        sonar.database.Tool.add(
            "vivado",
            "2017.2",
            "vivado",
            "vivado_hls",
            "vivado",
            textwrap.dedent(
                """\
            source xzy
            export this=foo
        """
            ),
        )

        tool = ("vivado", "2017.2")
        sonar.database.Tool.activate(tool, tool, tool)

        active = sonar.database.Tool.get_active()
        assert active["cad"] == tool
        assert active["sim"] == tool
        assert active["hls"] == tool

        file_str = open(
            sonar.core.include.Constants.SONAR_SHELL_TOOL_SOURCE, "r"
        ).read()
        assert file_str == textwrap.dedent(
            """\
            source xzy
            export this=foo
        """
        )


class TestBoard:
    """
    Test the board-related parts of the database
    """

    @pytest.fixture(autouse=True)
    def setup(self, call_sonar):
        """
        Verify that the database exists
        """
        # pylint: disable=attribute-defined-outside-init
        sonar.api.check_database()
        self.sonar = call_sonar

    def test_get(self):
        """
        Test 'get' for a board

        Args:
            call_sonar (CallSonar): Used to call sonar from Python
        """
        sonar.database.init()
        with pytest.raises(sonar.exceptions.SonarInvalidArgError):
            board = sonar.database.Board.get("fake_board")

        board_path = os.path.join(self.sonar.abs_path(), "sonar/boards/ad_8k5")
        sonar.database.Board.add(board_path)

        boards = sonar.database.Board.get()
        assert boards == {"ad_8k5": board_path}
        board = sonar.database.Board.get("ad_8k5")
        assert board == board_path

    def test_activate(self):
        """
        Test activating a board

        Args:
            call_sonar (CallSonar): Used to call sonar from Python
        """

        sonar.database.init()

        board_path = os.path.join(self.sonar.abs_path(), "sonar/boards/ad_8k5")
        sonar.database.Board.add(board_path)

        sonar.database.Board.activate("ad_8k5")
        active = sonar.database.Board.get_active()
        assert active == "ad_8k5"

        file_str = open(
            sonar.core.include.Constants.SONAR_SHELL_BOARD_SOURCE, "r"
        ).read()
        assert file_str == textwrap.dedent(
            """\
            export SONAR_BOARD_NAME=ad_8k5
            export SONAR_PART=xcku115-flva1517-2-e
            export SONAR_PART_FAMILY=Kintex_Ultrascale"""
        )


class TestRepo:
    """
    Test the repository-related parts of the database
    """

    @pytest.fixture(autouse=True)
    def setup(self, test_dir):
        """
        Verify that the database exists
        """
        # pylint: disable=attribute-defined-outside-init
        sonar.api.check_database()
        self.paths = test_dir.repos

    def test_get(self, monkeypatch):
        """
        Test 'get' for a repository

        Args:
            monkeypatch (MonkeyPatch): Defined in pytest for monkeypatching code
        """
        sonar.database.init()
        with pytest.raises(sonar.exceptions.SonarInvalidArgError):
            sonar.database.Repo.get("fake_repo")

        monkeypatch.setattr(toml, "load", mock_config)
        sonar.database.Repo.add(self.paths.valid)

        repos = sonar.database.Repo.get()
        assert repos == {"valid": {"path": self.paths.valid}}
        repo = sonar.database.Repo.get("valid")
        assert repo == {"path": self.paths.valid}

    def test_activate(self, monkeypatch):
        """
        Test 'get' for a repository

        Args:
            monkeypatch (MonkeyPatch): Defined in pytest for monkeypatching code
        """
        sonar.database.init()

        monkeypatch.setattr(toml, "load", mock_config)
        sonar.database.Repo.add(self.paths.valid)

        sonar.database.Repo.activate("valid")
        active = sonar.database.Repo.get_active()
        assert active == "valid"

        file_str = open(
            sonar.core.include.Constants.SONAR_SHELL_REPO_SOURCE, "r"
        ).read()
        assert file_str == textwrap.dedent(
            f"""\
            export SONAR_REPO={self.paths.valid}"""
        )


class TestEnv:
    """
    Test the environment-related parts of the database
    """

    @pytest.fixture(autouse=True)
    def setup(self, test_dir, call_sonar):
        """
        Verify that the database exists
        """
        # pylint: disable=attribute-defined-outside-init
        sonar.api.check_database()
        self.paths = test_dir.repos
        self.sonar = call_sonar

    @staticmethod
    def test_get():
        """
        Test 'get' for an environment
        """
        sonar.database.init()
        with pytest.raises(sonar.exceptions.SonarInvalidArgError):
            sonar.database.Env.get("fake_env")

        tool = ("vivado", "2017.2")
        sonar.database.Env.add("test_env", tool, tool, tool, "ad_8k5", "valid")

        envs = sonar.database.Env.get()
        assert envs == {
            "test_env": {
                "cad": tool,
                "hls": tool,
                "sim": tool,
                "board": "ad_8k5",
                "repo": "valid",
            }
        }
        env = sonar.database.Env.get("test_env")
        assert env == {
            "cad": tool,
            "hls": tool,
            "sim": tool,
            "board": "ad_8k5",
            "repo": "valid",
        }

    def test_activate(self, monkeypatch):
        """
        Test activating an environment

        Args:
            monkeypatch (MonkeyPatch): Defined in pytest for monkeypatching code
        """
        sonar.database.init()

        monkeypatch.setattr(toml, "load", mock_config)
        sonar.database.Repo.add(self.paths.valid)

        board_path = os.path.join(self.sonar.abs_path(), "sonar/boards/ad_8k5")
        sonar.database.Board.add(board_path)

        sonar.database.Tool.add(
            "vivado",
            "2017.2",
            "vivado",
            "vivado_hls",
            "vivado",
            textwrap.dedent(
                """\
            source xzy
            export this=foo
        """
            ),
        )

        tool = ("vivado", "2017.2")
        sonar.database.Env.add("test_env", tool, tool, tool, "ad_8k5", "valid")

        sonar.database.Env.activate("test_env")
        active = sonar.database.Env.get_active()
        assert active == "test_env"

        file_str = open(
            sonar.core.include.Constants.SONAR_SHELL_REPO_SOURCE, "r"
        ).read()
        assert file_str == textwrap.dedent(
            f"""\
            export SONAR_REPO={self.paths.valid}"""
        )

        file_str = open(
            sonar.core.include.Constants.SONAR_SHELL_BOARD_SOURCE, "r"
        ).read()
        assert file_str == textwrap.dedent(
            """\
            export SONAR_BOARD_NAME=ad_8k5
            export SONAR_PART=xcku115-flva1517-2-e
            export SONAR_PART_FAMILY=Kintex_Ultrascale"""
        )

        file_str = open(
            sonar.core.include.Constants.SONAR_SHELL_TOOL_SOURCE, "r"
        ).read()
        assert file_str == textwrap.dedent(
            """\
            source xzy
            export this=foo
        """
        )
