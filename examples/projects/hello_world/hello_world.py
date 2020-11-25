"""
The hello_world example testbench generation. This describes the most common
options in sonar to configure a testbench.
"""

from sonar.interfaces.axi4_lite_slave import AXI4LiteSlave
from sonar.interfaces.axi4_stream import AXI4Stream
from sonar.testbench import Module, Testbench, TestVector, Thread


def test_testbench_hello_world(test_dir, monkeypatch):
    """
    Define the testbench for the hello_world project from the examples. Note,
    these arguments are only used by pytest.

    Args:
        test_dir (TestPaths): Used to hold test directories
        monkeypatch (MonkeyPatch): Defined in pytest for monkeypatching code
    """
    # pylint: disable=too-many-statements

    # create top-level entity for the testbench using the default constructor
    # and set the Module_Name metadata tag to 'hello_world' as specified by the
    # default constructor.
    hello_world_tb = Testbench.default("hello_world")
    hello_world_tb.set_metadata("Timeout_Value", "1us")
    hello_world_tb.set_metadata("Headers", ["hello_world.hpp"])

    # the DUT -----------------------------------------------------------------

    # create a DUT module named 'DUT' and specify its signal ports
    dut = Module.cpp_vivado("DUT", "20.5ns")
    dut.add_port("state_out", size=3, direction="output")
    dut.add_port("ack", "output")
    clock = dut.ports.get_clocks("input")[0]  # we know only one clock exists
    reset = dut.ports.get_resets("input")[0]  # we know only one reset exists
    hello_world_tb.add_dut(dut)

    # create an AXI-M interface with the default side channels and a data width
    # of 64 and add it to the DUT.
    axis_out = AXI4Stream("axis_output", "master", clock)
    axis_out.init_signals("default", 64)
    axis_out.iClass = "axis_t"  # this field is needed for C++ TBs
    axis_out.flit = "axis_word_t"  # this field is needed for C++ TBs
    dut.add_interface(axis_out)

    # create an AXI-S interface with the default side channels and a data width
    # of 64 and add it to the DUT.
    axis_in = AXI4Stream("axis_input", "slave", clock)
    axis_in.init_signals("default", 64)
    axis_in.iClass = "axis_t"
    axis_in.flit = "axis_word_t"
    dut.add_interface(axis_in)

    # create a S-AXILite interface, set up its register space and add it to the
    # DUT.
    ctrl_bus = AXI4LiteSlave("s_axi_ctrl_bus", clock, reset)
    ctrl_bus.add_register("enable", 0x10)  # register 'enable' is at addr 0x10
    ctrl_bus.set_address("4K", 0)  # address range is 4K at an offset of 0
    ctrl_bus.init_signals(mode="default", data_width=32, addr_width=5)
    dut.add_interface(ctrl_bus)

    # test vectors ------------------------------------------------------------

    test_vector_0 = TestVector()

    # this thread just initializes signals. It could be reused in many test
    # vectors so it's created differently from the other threads.
    init_thread = Thread()
    init_thread.wait_negedge(clock.name)  # wait for negedge of the clock
    init_thread.init_signals()  # initialize all signals to zero
    init_thread.add_delay("40ns")
    init_thread.set_signal(reset.name, 1)
    init_thread.set_signal("axis_output_tready", 1)
    test_vector_0.add_thread(init_thread)

    # this thread is responsible for sending the stimulus (i.e. the driver)
    input_thr = test_vector_0.add_thread()
    input_thr.add_delay("100ns")
    input_thr.init_timer()  # zeros a timer that can be evaluated for runtime
    ctrl_bus.write(input_thr, "enable", 1)
    axis_in.write(input_thr, 0xABCD)
    input_thr.call_dut(2)
    input_thr.wait_level("ack == $0", 1)
    axis_in.write(input_thr, 0)
    input_thr.call_dut(3)
    input_thr.wait_level("ack == $0", 1)
    input_thr.add_delay("110ns")
    input_thr.set_flag(0)  # sets flag 0 that another thread may be waiting on

    # this thread will validate the behavior of the DUT (i.e. the monitor)
    output_thr = test_vector_0.add_thread()
    axis_out.read(output_thr, 1)  # AXIS implicitly waits for valid data
    output_thr.wait_flag(0)  # waits for flag 0 to be set by another thread
    ctrl_bus.read(output_thr, "enable", 1)
    output_thr.print_elapsed_time(
        "End"
    )  # prints string + time since last init
    output_thr.display("The_simulation_is_finished")  # prints string
    output_thr.end_vector()  # terminates the test vector

    # epilogue -----------------------------------------------------------------

    # if there are many vectors, they can be selectively enabled by adding them
    hello_world_tb.add_test_vector(test_vector_0)

    # generate the output testbenches and data files for the specified languages
    # at the designated path
    if monkeypatch:
        monkeypatch.setenv("SONAR_CAD_VERSION", str(2018.1))
    if test_dir:
        hello_world_tb.generate_tb(
            str(test_dir.testbench.hello_world.joinpath("hello_world.py")),
            "all",
        )
        print(hello_world_tb)
    else:
        hello_world_tb.generate_tb(__file__, "all", True)


if __name__ == "__main__":
    test_testbench_hello_world(None, None)
