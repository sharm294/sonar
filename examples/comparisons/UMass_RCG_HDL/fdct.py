import os

from sonar.testbench import Testbench, Module, TestVector


# create top-level entity for the testbench using the default constructor
# and set the Module_Name metadata tag to 'sample' as specified by the
# default constructor.
fdct_tb = Testbench.default("fdct")
filepath = os.path.join(os.path.dirname(__file__), "build/")

# the DUT ------------------------------------------------------------------

# create a DUT module named 'DUT' and specify its signal ports
dut = Module.default("DUT")
dut.add_clock_port("clk", "5ns")
dut.add_reset_port("rst")
dut.add_port("din", size=8, direction="input")
dut.add_port("ena", direction="input")
dut.add_port("dout", size=12, direction="output")
dut.add_port("douten", direction="output")
dut.add_parameter("coef_width", 13)

fdct_tb.add_module(dut)

# test vectors -------------------------------------------------------------

test_vector_0 = TestVector()

thread_0 = test_vector_0.add_thread()
thread_0.init_signals()
thread_0.set_signal("ena", 1)
thread_0.add_delay("17ns")
thread_0.set_signal("rst", 1)
for i in range(20):
    thread_0.wait_posedge("clk")
thread_0.set_signal("dstrb", 1)
thread_0.wait_posedge("clk")
thread_0.set_signal("dstrb", 0)

# fmt: off
input_array = [
    139, 144, 149, 153, 155, 155, 155, 155, 144, 151, 153, 156, 159, 156, 156,
    156, 150, 155, 160, 163, 158, 156, 156, 156, 159, 161, 162, 160, 160, 159,
    159, 159, 159, 160, 161, 162, 162, 155, 155, 155, 161, 161, 161, 161, 160,
    157, 157, 157, 162, 162, 161, 163, 162, 157, 157, 157, 162, 162, 161, 161,
    163, 158, 158, 158
]

output_array = [
    0x1d7, 0xffe, 0xfd3, 0xfea, 0xfdd, 0xfe8, 0xff6, 0xff4, 0xfed, 0xff2, 0xfff,
    0xffc, 0xffd, 0xffa, 0x004, 0xffd, 0xffa, 0x003, 0x000, 0xffe, 0x004, 0xffd,
    0x000, 0x003, 0x003, 0x000, 0x000, 0xffb, 0x003, 0x001, 0xffe, 0x002, 0x003,
    0x003, 0xfff, 0xffb, 0x003, 0xfff, 0xfff, 0x000, 0x000, 0xfff, 0xffe, 0x000,
    0x000, 0xfff, 0xffe, 0xffd, 0xff8, 0xffc, 0xfff, 0x003, 0x001, 0x001, 0x003,
    0x002, 0x003, 0x004, 0x002, 0x002, 0xffe, 0xffe, 0xfff, 0xfff
]
# fmt: on

for y in range(8):
    for x in range(8):
        thread_0.set_signal("din", input_array[y * 8 + x] - 128)
        thread_0.wait_posedge("clk")

# wait for douten
thread_0.wait_level("douten == 1")
thread_0.wait_posedge("clk")

for y in range(8):
    for x in range(8):
        thread_0.wait("assert(dout == $value)", output_array[y * 8 + x])

thread_0.end_vector()  # terminates the test vector

# epilogue -----------------------------------------------------------------

# if there are many vectors, they can be selectively enabled by adding them
fdct_tb.add_test_vector(test_vector_0)

# generate the output testbenches and data files for the specified languages
# at the designated path
fdct_tb.generate_tb(filepath, "sv")
