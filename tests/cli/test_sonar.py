from sonar.exceptions import ReturnValue
from sonar.include import Constants


def test_no_args(capsys, call_sonar):
    exit_code = call_sonar.cli()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert exit_code == Constants.ARGPARSE_FAILURE


def test_help(capsys, call_sonar):
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
    exit_code = call_sonar.cli("--bad_arg")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert exit_code == Constants.ARGPARSE_FAILURE


def test_bad_command(capsys, call_sonar):
    exit_code = call_sonar.cli("bad_arg")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert exit_code == Constants.ARGPARSE_FAILURE
