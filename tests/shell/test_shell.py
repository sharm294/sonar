import os
import subprocess


def test_shell_sample(call_sonar):
    run_script = os.path.join(call_sonar.abs_path(), "tests/shell/test.sh")
    test_script = os.path.join(call_sonar.abs_path(), "tests/shell/sample/test.sh")
    test_dir = os.path.join(call_sonar.abs_path(), "tests/shell/sample")
    subprocess.run([run_script, test_script, test_dir], check=True)
