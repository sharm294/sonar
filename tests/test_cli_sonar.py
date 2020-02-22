from sonar.include import ReturnValue


def test_sonar(call_sonar):
    exit_code = call_sonar.cli()
    assert exit_code == ReturnValue.SONAR_OK


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


def test_bad_arg(capsys, call_sonar):
    exit_code = call_sonar.cli("--bad_arg")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert exit_code == 2  # argparse returns 2 on ArgumentParse error


def test_bad_command(capsys, call_sonar):
    exit_code = call_sonar.cli("bad_arg")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert exit_code == 2  # argparse returns 2 on ArgumentParse error
