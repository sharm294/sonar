"""
Test environment activation
"""

from sonar.exceptions import ReturnValue


def test_activate_fake_env(call_sonar):
    """
    Attempts to activate a non-existent environment

    Args:
        call_sonar (CallSonar): used to call sonar from Python
    """
    exit_code = call_sonar.cli("activate fake_env")
    assert exit_code == ReturnValue.SONAR_INVALID_ARG
