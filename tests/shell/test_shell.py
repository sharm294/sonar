import os
import subprocess


def test_shell_sample(call_sonar):
    test_dir = os.path.join(call_sonar.abs_path(), "tests/shell/sample")
    subprocess.run(
        ["./tests/shell/test.sh", "./tests/shell/sample/test.sh", test_dir], check=True
    )
    assert False


# src/axi_vip_v1_1_2/axi_vip_v1_1_vlsyn_rfs.sv
# src/vip_bd_1_axi_vip_0_0.sv
# src/vip_bd_0_axi_vip_0_0.sv
# src/vip_bd_1_axi_vip_0_0_ooc.xdc
# src/vip_bd_0_axi_vip_0_0_ooc.xdc

# sim/vip_bd_1_axi_vip_0_0_pkg.sv
# sim/vip_bd_0_axi_vip_0_0_pkg.sv
# sim/axi_vip_v1_1_2/axi_vip_v1_1_rfs.sv
# sim/vip_bd_1_axi_vip_0_0.sv
# sim/vip_bd_0_axi_vip_0_0.sv
