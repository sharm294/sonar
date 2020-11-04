"""
Test basic functionality of the CLI
"""

from sonar.core.include import Constants
from sonar.exceptions import ReturnValue


def test_no_args(capsys, call_sonar):
    """
    Attempt to call with no arguments

    Args:
        capsys (Capsys): Defined in pytest for capturing stdout and stderr
        call_sonar (CallSonar): Used to call sonar from Python
    """
    exit_code = call_sonar.cli()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert exit_code == Constants.ARGPARSE_FAILURE


def test_help(capsys, call_sonar):
    """
    Test passing in '--help'

    Args:
        capsys (Capsys): Defined in pytest for capturing stdout and stderr
        call_sonar (CallSonar): Used to call sonar from Python
    """
    exit_code = call_sonar.cli("--help")
    captured = capsys.readouterr()
    assert captured.out != ""
    assert captured.err == ""
    assert exit_code == ReturnValue.SONAR_OK

    exit_code = call_sonar.cli("-h")
    captured = capsys.readouterr()
    assert captured.out != ""
    assert captured.err == ""
    assert exit_code == ReturnValue.SONAR_OK


def test_version(capsys, call_sonar):
    """
    Test passing in '--version'

    Args:
        capsys (Capsys): Defined in pytest for capturing stdout and stderr
        call_sonar (CallSonar): Used to call sonar from Python
    """
    exit_code = call_sonar.cli("--version")
    captured = capsys.readouterr()
    assert captured.out != ""
    assert captured.err == ""
    assert exit_code == ReturnValue.SONAR_OK

    exit_code = call_sonar.cli("-v")
    captured = capsys.readouterr()
    assert captured.out != ""
    assert captured.err == ""
    assert exit_code == ReturnValue.SONAR_OK


def test_bad_option(capsys, call_sonar):
    """
    Attempt to pass a non-existent option

    Args:
        capsys (Capsys): Defined in pytest for capturing stdout and stderr
        call_sonar (CallSonar): Used to call sonar from Python
    """
    exit_code = call_sonar.cli("--bad_arg")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert exit_code == Constants.ARGPARSE_FAILURE


def test_bad_command(capsys, call_sonar):
    """
    Attempt to pass a bad command

    Args:
        capsys (Capsys): Defined in pytest for capturing stdout and stderr
        call_sonar (CallSonar): Used to call sonar from Python
    """
    exit_code = call_sonar.cli("bad_arg")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert exit_code == Constants.ARGPARSE_FAILURE
