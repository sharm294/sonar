import pytest

from sonar.exceptions import ReturnValue
import sonar.database as Database


class TestVivado:
    @pytest.fixture(autouse=True)
    def setup(self, test_dir, call_sonar):
        self.paths = test_dir.vivado
        self.sonar = call_sonar.cli

    def test_vivado_fake_path(self):
        exit_code = self.sonar("init vivado " + str(self.paths.non_existent))
        assert exit_code == ReturnValue.SONAR_NONEXISTENT_PATH

    def test_vivado_no_vivado(self):
        exit_code = self.sonar("init vivado " + str(self.paths.no_vivado))
        assert exit_code == ReturnValue.SONAR_INVALID_PATH

    def test_vivado_one_vivado(self):
        exit_code = self.sonar("init vivado " + str(self.paths.one_vivado))
        assert exit_code == ReturnValue.SONAR_OK
        env = Database.Env.get()
        assert "vivado_2017.2" in env

    def test_vivado_many_vivado(self):
        exit_code = self.sonar("init vivado " + str(self.paths.many_vivado))
        assert exit_code == ReturnValue.SONAR_OK
        env = Database.Env.get()
        assert "vivado_2017.3" in env
        assert "vivado_2018.2" in env
