import os

from sonar.interfaces.axi4_lite_slave import AXI4LiteSlave
from sonar.testbench import Module, Testbench, TestVector, Thread

# create top-level entity for the testbench using the default constructor
# and set the Module_Name metadata tag to 'fdct' as specified by the
# default constructor.
axi_lite_tb = Testbench.default("fdct")
filepath = os.path.join(os.path.dirname(__file__), "build/")

# the DUT ------------------------------------------------------------------

# create a DUT module named 'DUT' and specify its signal ports
dut = Module.default("DUT")
dut.add_clock_port("clk", "5ns")
dut.add_reset_port("rst")

ctrl_bus = AXI4LiteSlave("s_axi_ctrl_bus", "clk", "rst")
ctrl_bus.add_register("reg_0", 0x0)  # register 'reg_0' is at 0x0
ctrl_bus.add_register("reg_1", 0x1)  # register 'reg_1' is at 0x1
ctrl_bus.set_address("4K", 0)  # address range is 4K at an offset of 0
ctrl_bus.init_signals(mode="default", data_width=32, addr_width=32)
dut.add_interface(ctrl_bus)

axi_lite_tb.add_module(dut)

# test vectors -------------------------------------------------------------

test_vector_0 = TestVector()

thread_0 = Thread()
thread_0.init_signals()
thread_0.set_signal("rst", 1)
for i in range(10):
    thread_0.wait_posedge("clk")
thread_0.set_signal("rst", 0)
test_vector_0.add_thread(thread_0)

thread_1 = test_vector_0.add_thread()
ctrl_bus.write(thread_1, "reg_0", 2)
ctrl_bus.read(thread_1, "reg_0", 2)

thread_0.end_vector()  # terminates the test vector

# epilogue -----------------------------------------------------------------

# if there are many vectors, they can be selectively enabled by adding them
axi_lite_tb.add_test_vector(test_vector_0)

# generate the output testbenches and data files for the specified languages
# at the designated path
axi_lite_tb.generate_tb(filepath, "sv")
