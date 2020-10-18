import os
import pytest
import textwrap
import toml

import sonar.api
import sonar.database
import sonar.exceptions
import sonar.core.include


def test_find_fpga_family():
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


class TestTool:
    @pytest.fixture(autouse=True)
    def setup(self):
        sonar.api.check_database()

    def test_get(self):
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
            "executable": {"cad": "vivado", "hls": "vivado_hls", "sim": "vivado"},
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
            "executable": {"cad": "vivado", "hls": "vivado_hls", "sim": "vivado"},
            "script": {
                "2017.2": "source xzy\nexport this=foo\n",
                "2017.3": "source zyx\nexport this=bar\n",
            },
        }

    def test_activate(self):
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

        file_str = open(sonar.core.include.Constants.SONAR_SHELL_TOOL_SOURCE, "r").read()
        assert file_str == textwrap.dedent(
            """\
            source xzy
            export this=foo
        """
        )


class TestBoard:
    @pytest.fixture(autouse=True)
    def setup(self):
        sonar.api.check_database()

    def test_get(self, call_sonar):
        sonar.database.init()
        with pytest.raises(sonar.exceptions.SonarInvalidArgError):
            board = sonar.database.Board.get("fake_board")

        board_path = os.path.join(call_sonar.abs_path(), "sonar/boards/ad_8k5")
        sonar.database.Board.add(board_path)

        boards = sonar.database.Board.get()
        assert boards == {"ad_8k5": board_path}
        board = sonar.database.Board.get("ad_8k5")
        assert board == board_path

    def test_activate(self, call_sonar):
        sonar.database.init()

        board_path = os.path.join(call_sonar.abs_path(), "sonar/boards/ad_8k5")
        sonar.database.Board.add(board_path)

        sonar.database.Board.activate("ad_8k5")
        active = sonar.database.Board.get_active()
        assert active == "ad_8k5"

        file_str = open(sonar.core.include.Constants.SONAR_SHELL_BOARD_SOURCE, "r").read()
        assert file_str == textwrap.dedent(
            """\
            export SONAR_BOARD_NAME=ad_8k5
            export SONAR_PART=xcku115-flva1517-2-e
            export SONAR_PART_FAMILY=Kintex_Ultrascale"""
        )


class TestRepo:
    @pytest.fixture(autouse=True)
    def setup(self):
        sonar.api.check_database()

    def test_get(self, test_dir, monkeypatch):
        sonar.database.init()
        with pytest.raises(sonar.exceptions.SonarInvalidArgError):
            sonar.database.Repo.get("fake_repo")

        def mock_config(path):
            return {"project": {"name": "valid"}}

        monkeypatch.setattr(toml, "load", mock_config)
        sonar.database.Repo.add(test_dir.repos.valid)

        repos = sonar.database.Repo.get()
        assert repos == {"valid": {"path": test_dir.repos.valid}}
        repo = sonar.database.Repo.get("valid")
        assert repo == {"path": test_dir.repos.valid}

    def test_activate(self, test_dir, monkeypatch):
        sonar.database.init()

        def mock_config(path):
            return {"project": {"name": "valid"}}

        monkeypatch.setattr(toml, "load", mock_config)
        sonar.database.Repo.add(test_dir.repos.valid)

        sonar.database.Repo.activate("valid")
        active = sonar.database.Repo.get_active()
        assert active == "valid"

        file_str = open(sonar.core.include.Constants.SONAR_SHELL_REPO_SOURCE, "r").read()
        assert file_str == textwrap.dedent(
            f"""\
            export SONAR_REPO={test_dir.repos.valid}"""
        )


class TestEnv:
    @pytest.fixture(autouse=True)
    def setup(self):
        sonar.api.check_database()

    def test_get(self, test_dir, monkeypatch):
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

    def test_activate(self, call_sonar, test_dir, monkeypatch):
        sonar.database.init()

        def mock_config(path):
            return {"project": {"name": "valid"}}

        monkeypatch.setattr(toml, "load", mock_config)
        sonar.database.Repo.add(test_dir.repos.valid)

        board_path = os.path.join(call_sonar.abs_path(), "sonar/boards/ad_8k5")
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

        file_str = open(sonar.core.include.Constants.SONAR_SHELL_REPO_SOURCE, "r").read()
        assert file_str == textwrap.dedent(
            f"""\
            export SONAR_REPO={test_dir.repos.valid}"""
        )

        file_str = open(sonar.core.include.Constants.SONAR_SHELL_BOARD_SOURCE, "r").read()
        assert file_str == textwrap.dedent(
            """\
            export SONAR_BOARD_NAME=ad_8k5
            export SONAR_PART=xcku115-flva1517-2-e
            export SONAR_PART_FAMILY=Kintex_Ultrascale"""
        )

        file_str = open(sonar.core.include.Constants.SONAR_SHELL_TOOL_SOURCE, "r").read()
        assert file_str == textwrap.dedent(
            """\
            source xzy
            export this=foo
        """
        )
