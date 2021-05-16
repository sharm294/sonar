"""
The ethernet example testbench generation. This demonstrates how to use layers
to send data to a DUT.
"""

from sonar.interfaces.axi4_stream import AXI4Stream
from sonar.layers.ethernet import Ethernet
from sonar.testbench import Module, Testbench, TestVector, Thread


def test_testbench_ethernet(test_dir, monkeypatch):
    """
    Define the testbench for the ethernet project from the examples. Note,
    these arguments are only used by pytest.

    Args:
        test_dir (TestPaths): Used to hold test directories
        monkeypatch (MonkeyPatch): Defined in pytest for monkeypatching code
    """
    # pylint: disable=too-many-statements,too-many-locals

    # create top-level entity for the testbench using the default constructor
    # and set the Module_Name metadata tag to 'ethernet' as specified by the
    # default constructor.
    ethernet_tb = Testbench.default("ethernet")
    ethernet_tb.set_metadata("Timeout_Value", "1us")

    # the DUT -----------------------------------------------------------------

    # create a DUT module named 'DUT' and specify its signal ports
    dut = Module.default("DUT")
    data_width = 64
    dut.add_parameter("DATA_WIDTH", data_width)
    dut.add_clock_port("clk", "20ns")
    dut.add_reset_port("rst")
    dut.add_port("m_eth_hdr_valid", "output")
    dut.add_port("m_eth_hdr_ready", "input")
    dut.add_port("m_eth_dest_mac", "output", size=48)
    dut.add_port("m_eth_src_mac", "output", size=48)
    dut.add_port("m_eth_type", "output", size=16)
    dut.add_port("busy", "output")
    dut.add_port("error_header_early_termination", "output")
    ethernet_tb.add_dut(dut)

    # create an AXI4Stream-M interface with the default side channels + tkeep
    axis_out = AXI4Stream("m_eth_payload_axis", "master", "clk", "rst")
    axis_out.init_signals("tkeep", 64, False)
    axis_out.add_endpoint("manual")
    dut.add_interface(axis_out)

    # create an AXI4Stream-S interface with the default side channels + tkeep
    axis_in = AXI4Stream("s_axis", "slave", "clk", "rst")
    axis_in.init_signals("tkeep", 64, False)
    axis_in.add_endpoint("manual")
    dut.add_interface(axis_in)

    # test vectors ------------------------------------------------------------

    test_vector_0 = TestVector()

    # this thread just initializes signals. It could be reused in many test
    # vectors so it's created differently from the other threads.
    init_thread = Thread()
    init_thread.wait_negedge("clk")  # wait for negedge of clk
    init_thread.init_signals()  # initialize all signals to zero
    init_thread.set_signal("rst", 1)
    init_thread.add_delay("40ns")
    init_thread.set_signal("rst", 0)
    init_thread.set_signal("m_eth_hdr_ready", 1)
    init_thread.set_signal("m_eth_payload_axis_tready", 1)
    ethernet_tb.set_prologue_thread(init_thread)

    # this thread is responsible for sending the stimulus (i.e. the driver)
    input_thr = test_vector_0.add_thread()
    input_thr.init_timer()  # zeros a timer that can be evaluated for runtime

    mac_src = "01:02:03:04:05:06"
    mac_dst = "07:08:09:0a:0b:0c"
    ether_type = "ba:ba"
    padstr = bytes(range(64))

    my_eth = Ethernet(mac_src, mac_dst, ether_type)
    my_eth.add_payload(padstr)
    my_eth.stream(input_thr, axis_in)

    # this thread will validate the behavior of the DUT (i.e. the monitor)
    header_thr = test_vector_0.add_thread()
    header_thr.wait_level("m_eth_hdr_valid == 1")
    header_thr.assert_value("m_eth_src_mac == 48'h010203040506")
    header_thr.assert_value("m_eth_dest_mac == 48'h0708090a0b0c")
    header_thr.assert_value("m_eth_type == 16'hbaba")

    payload_thr = test_vector_0.add_thread()
    my_eth.stream(payload_thr, axis_out, "payload")
    payload_thr.print_elapsed_time("End")
    payload_thr.end_vector()  # terminates the test vector

    # epilogue -----------------------------------------------------------------

    # if there are many vectors, they can be selectively enabled by adding them
    ethernet_tb.add_test_vector(test_vector_0)

    # generate the output testbenches and data files for the specified languages
    # at the designated path
    if monkeypatch:
        monkeypatch.setenv("SONAR_CAD_VERSION", str(2018.1))
    if test_dir:
        ethernet_tb.generate_tb(
            str(test_dir.testbench.ethernet.joinpath("ethernet.py")),
            "sv",
            True,
        )
        print(ethernet_tb)  # used to test printing out the configuration
    else:
        ethernet_tb.generate_tb(__file__, "sv", True)


if __name__ == "__main__":
    # import scapy.layers.l2 as L2
    # ether_packet = L2.Ether(src=mac_src, dst=mac_dst, type=ether_type)
    # padstr = b"\x1A" * 62 # pad out packet so that it fits evenly in 64-bit bus
    # ether_packet.add_payload(padstr)
    # print(ether_packet)
    # print(len(ether_packet))
    # # with open(test_file_name, "wb") as f:
    # #     f.write(str(ether_packet))

    test_testbench_ethernet(None, None)
