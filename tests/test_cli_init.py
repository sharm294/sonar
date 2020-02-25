from sonar.exceptions import ReturnValue
from sonar.database import Database


def test_vivado_fake_path(call_sonar, test_vivado_path):
    exit_code = call_sonar.cli("init vivado " + str(test_vivado_path.non_existent))
    assert exit_code == ReturnValue.SONAR_NONEXISTENT_PATH


def test_vivado_no_vivado(call_sonar, test_vivado_path):
    exit_code = call_sonar.cli("init vivado " + str(test_vivado_path.no_vivado))
    assert exit_code == ReturnValue.SONAR_INVALID_PATH


def test_vivado_one_vivado(call_sonar, test_vivado_path):
    exit_code = call_sonar.cli("init vivado " + str(test_vivado_path.one_vivado))
    assert exit_code == ReturnValue.SONAR_OK
    env = Database.Env.get()
    assert "vivado_2017.2" in env


def test_vivado_many_vivado(call_sonar, test_vivado_path):
    exit_code = call_sonar.cli("init vivado " + str(test_vivado_path.many_vivado))
    assert exit_code == ReturnValue.SONAR_OK
    env = Database.Env.get()
    assert "vivado_2017.3" in env
    assert "vivado_2018.2" in env
