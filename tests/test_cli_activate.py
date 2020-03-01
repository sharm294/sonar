from sonar.exceptions import ReturnValue


def test_activate_fake_env(call_sonar):
    exit_code = call_sonar.cli("env activate fake_env")
    assert exit_code == ReturnValue.SONAR_INVALID_ARG
