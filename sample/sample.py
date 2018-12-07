import sys

from sonar import sonar as sonarTB
from sonar.interfaces import AXIS
from sonar.interfaces import SAXILite

def sample(folderpath, languages):

    sonar = sonarTB.Sonar.default('sample')
    sonar.set_metadata('Module_Name', 'sample')

    dut = sonarTB.Module.default("DUT")
    dut.add_clock_port("ap_clk", "20ns")
    dut.add_reset_port("ap_rst_n")
    dut.add_port("state_out_V", size=3, direction="output")
    dut.add_port("ack_V", direction="output")
    sonar.add_module(dut)

    axis_out = AXIS("axis_output", "master", "ap_clk")
    axis_out.port.init_channels('default', 64)
    axis_out.port.c_stream = "uaxis_l"
    axis_out.port.c_struct = "axis_word"
    # axis_out.ports.addChannel('TKEEP', 'tkeep', 8) # e.g. to add a new channel
    dut.add_interface(axis_out)

    axis_in = AXIS("axis_input", "slave", "ap_clk")
    axis_in.port.init_channels('default', 64)
    axis_in.port.c_stream = "uaxis_l"
    axis_in.port.c_struct = "axis_word"
    dut.add_interface(axis_in)

    ctrl_bus = SAXILite('s_axi_ctrl_bus', 'ap_clk', 'ap_rst_n')
    ctrl_bus.add_register('enable', 0x10)
    ctrl_bus.set_address('4K', 0)
    ctrl_bus.port.init_channels(mode='default', dataWidth=32, addrWidth=5)
    dut.add_interface(ctrl_bus)

    test_vector_0 = sonarTB.TestVector()

    initT = sonarTB.Thread()
    initT.wait_edge(False, 'ap_clk')
    initT.init_signals()
    initT.add_delay('40ns')
    initT.set_signal('ap_rst_n', 1)
    initT.set_signal('axis_output_tready', 1)
    test_vector_0.addThread(initT)

    inputT = sonarTB.Thread()
    inputT.add_delay('100ns')
    inputT.init_timer()
    inputT.add_transaction(ctrl_bus.write('enable', 1))
    inputT.add_transaction(axis_in.write(tdata=0xABCD, callTB=2))
    inputT.wait_level('ack_V == $value', value=1)
    inputT.add_transaction(axis_in.write(tdata=0,callTB=3))
    inputT.wait_level('ack_V == $value', value=1)
    inputT.add_delay('110ns')
    inputT.set_flag(0)
    test_vector_0.addThread(inputT)

    outputT = sonarTB.Thread()
    outputT.add_transaction(axis_out.read(tdata=1))
    outputT.wait_flag(0)
    outputT.add_transaction(ctrl_bus.read('enable', 1))
    outputT.print_elapsed_time('End')
    outputT.display('The_simulation_is_finished')
    outputT.end_vector()
    test_vector_0.addThread(outputT)

    sonar.add_test_vector(test_vector_0)
    sonar.finalize_waits()

    sonar.generateTB(folderpath, languages)

if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "-h" or arg == "--help":
            print("Usage: python sample.py folderpath languages")
            print("  folderpath: absolute path (with trailing /) to save files")
            print("  languages: all (SV + C) or sv (just SV)")

    if (len(sys.argv) == 3):
        sample(sys.argv[1], sys.argv[2])
    else:
        print("Incorrect number of arguments. Use -h or --help")
