import sys

from sonar.testbench import Testbench, Module, TestVector, Thread
from sonar.interfaces import AXIS, SAXILite


def sample(folderpath, languages):

    # create top-level entity for the testbench using the default constructor
    # and set the Module_Name metadata tag to 'sample' as specified by the
    # default constructor.
    sample_TB = Testbench.default("sample")

    # the DUT ------------------------------------------------------------------

    # create a DUT module named 'DUT' and specify its signal ports
    dut = Module.default("DUT")
    dut.add_clock_port("ap_clk", "20ns")
    dut.add_reset_port("ap_rst_n")
    dut.add_port("state_out_V", size=3, direction="output")
    dut.add_port("ack_V", direction="output")
    sample_TB.add_module(dut)

    # create an AXI-M interface with the default side channels and a data width
    # of 64 and add it to the DUT.
    axis_out = AXIS("axis_output", "master", "ap_clk")
    axis_out.port.init_channels("default", 64)
    axis_out.port.c_stream = "uaxis_l"  # this field is needed for C++ TBs
    axis_out.port.c_struct = "axis_word"  # this field is needed for C++ TBs
    # axis_out.ports.addChannel('TKEEP', 'tkeep', 8) # e.g. to add a new channel
    dut.add_interface(axis_out)

    # create an AXI-S interface with the default side channels and a data width
    # of 64 and add it to the DUT.
    axis_in = AXIS("axis_input", "slave", "ap_clk")
    axis_in.port.init_channels("default", 64)
    axis_in.port.c_stream = "uaxis_l"
    axis_in.port.c_struct = "axis_word"
    dut.add_interface(axis_in)

    # create a S-AXILite interface, set up its register space and add it to the
    # DUT.
    ctrl_bus = SAXILite("s_axi_ctrl_bus", "ap_clk", "ap_rst_n")
    ctrl_bus.add_register("enable", 0x10)  # register 'enable' is at 0x10
    ctrl_bus.set_address("4K", 0)  # address range is 4K at an offset of 0
    ctrl_bus.port.init_channels(mode="default", dataWidth=32, addrWidth=5)
    dut.add_interface(ctrl_bus)

    # test vectors -------------------------------------------------------------

    test_vector_0 = TestVector()

    # this thread just initializes signals. It could be reused in many test
    # vectors so it's created differently from the other threads.
    initT = Thread()
    initT.wait_negedge("ap_clk")  # wait for negedge of ap_clk
    initT.init_signals()  # initialize all signals to zero
    initT.add_delay("40ns")
    initT.set_signal("ap_rst_n", 1)
    initT.set_signal("axis_output_tready", 1)
    test_vector_0.add_thread(initT)

    # this thread is responsible for sending the stimulus (i.e. the driver)
    inputT = test_vector_0.add_thread()
    inputT.add_delay("100ns")
    inputT.init_timer()  # zeros a timer that can be evaluated for runtime
    ctrl_bus.write(inputT, "enable", 1)
    axis_in.write(inputT, 0xABCD, callTB=2)  # callTB is used in C++ TBs
    inputT.wait_level("ack_V == $value", value=1)
    axis_in.write(inputT, 0, callTB=3)
    inputT.wait_level("ack_V == $value", value=1)
    inputT.add_delay("110ns")
    inputT.set_flag(0)  # sets flag 0 that another thread may be waiting on

    # this thread will validate the behavior of the DUT (i.e. the monitor)
    outputT = test_vector_0.add_thread()
    axis_out.read(outputT, 1)  # AXIS implicitly waits for valid data
    outputT.wait_flag(0)  # waits for flag 0 to be set by another thread
    ctrl_bus.read(outputT, "enable", 1)
    outputT.print_elapsed_time("End")  # prints string + time since last init
    outputT.display("The_simulation_is_finished")  # prints string
    outputT.end_vector()  # terminates the test vector

    # epilogue -----------------------------------------------------------------

    # if there are many vectors, they can be selectively enabled by adding them
    sample_TB.add_test_vector(test_vector_0)

    # generate the output testbenches and data files for the specified languages
    # at the designated path
    sample_TB.generateTB(folderpath, languages)


if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "-h" or arg == "--help":
            print("Usage: python sample.py folderpath languages")
            print("  folderpath: absolute path (with trailing /) to save files")
            print("  languages: all (SV + C) or sv (just SV)")

    if len(sys.argv) == 3:
        sample(sys.argv[1], sys.argv[2])
    else:
        print("Incorrect number of arguments. Use -h or --help")
