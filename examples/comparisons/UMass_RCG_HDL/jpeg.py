import os

from sonar.testbench import Testbench, Module, TestVector


# create top-level entity for the testbench using the default constructor
# and set the Module_Name metadata tag to 'jpeg' as specified by the
# default constructor.
jpeg_tb = Testbench.default("jpeg")
filepath = os.path.join(os.path.dirname(__file__), "build/")

# the DUT ------------------------------------------------------------------

# create a DUT module named 'DUT' and specify its signal ports
dut = Module.default("DUT")
dut.add_clock_port("clk", "5ns")
dut.add_reset_port("rst")
dut.add_port("din", size=8, direction="input")
dut.add_port("dstrb", direction="input")
dut.add_port("qnt_val", size=8, direction="input")
dut.add_port("ena", direction="input")
dut.add_port("qnt_cnt", size=6, direction="output")
dut.add_port("size", size=4, direction="output")
dut.add_port("rlen", size=4, direction="output")
dut.add_port("amp", size=12, direction="output")
dut.add_port("douten", direction="output")
dut.add_parameter("coef_width", 13)

jpeg_tb.add_module(dut)

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
    163, 158, 158, 158, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 70, 72, 70,
    70, 72, 68, 68, 64, 103, 101, 103, 100, 99, 97, 94, 94, 132, 132, 132, 130,
    129, 129, 125, 121, 157, 157, 155, 154, 153, 150, 148, 145, 168, 163, 164,
    162, 163, 161, 161, 156, 172, 170, 165, 166, 163, 163, 162, 158, 174, 170,
    167, 167, 164, 163, 164, 159, 174, 173, 170, 167, 167, 166, 166, 160, 151,
    147, 152, 140, 138, 125, 136, 160, 157, 148, 152, 137, 124, 105, 108, 144,
    152, 151, 146, 128, 99, 73, 75, 116, 154, 148, 145, 111, 91, 68, 62, 98,
    156, 144, 147, 93, 97, 105, 61, 82, 155, 139, 149, 76, 101, 140, 59, 74,
    148, 135, 147, 71, 114, 158, 79, 66, 135, 120, 133, 92, 133, 176, 103, 60
]

qnt_list = [
    16, 11, 12, 14, 12, 10, 16, 14, 13, 14, 18, 17, 16, 19, 24, 40, 26, 24, 22,
    22, 24, 49, 35, 37, 29, 40, 58, 51, 61, 60, 57, 51, 56, 55, 64, 72, 92, 78,
    64, 68, 87, 69, 55, 56, 80, 109, 81, 87, 95, 98, 103, 104, 103, 62, 77,
    113, 121, 112, 100, 120, 92, 101, 103, 99
]

output_array = [
    0x00f, 0x000, 0x7fe, 0x7ff, 0x7ff, 0x7ff, 0x000, 0x000, 0x7ff, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x7c0, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x005, 0x002,
    0x7eb, 0x7f8, 0x000, 0x000, 0x000, 0x000, 0x000, 0x7fd, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x7fc, 0x00e, 0x005, 0x005, 0x7ff, 0x002, 0x001, 0x003,
    0x7fb, 0x001, 0x000, 0x000, 0x7fe, 0x7fb, 0x7ff, 0x7ff, 0x002, 0x002,
    0x000, 0x7ff, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x001,
    0x000, 0x7ff, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000,
    0x000, 0x000, 0x000, 0x000, 0x000, 0x000
]
# fmt: on


input_lists_start = 0
input_lists_end = 3
list_cnt = input_lists_start * 64
output_lists_start = 1
output_lists_end = 1

for n in range(input_lists_end):
    thread_0.add_delay("1ns")
    thread_0.set_signal("dstrb", 1)
    for y in range(8):
        for x in range(8):
            thread_0.wait_posedge("clk")
            thread_0.add_delay("1ns")
            thread_0.set_signal("dstrb", 0)
            thread_0.set_signal("din", input_array[list_cnt] - 128)
            list_cnt += 1

# wait for douten
thread_0.wait_level("douten == 1")
thread_0.wait_posedge("clk")

for y in range(8):
    for x in range(8):
        thread_0.wait("assert(dout == $value)", output_array[y * 8 + x])

thread_0.set_flag(0)

thread_0.end_vector()  # terminates the test vector

# thread_1 = test_vector_0.add_thread()
# thread_1.wait_posedge("clk")
# thread_1.set_signal("qnt_val", qnt_list[qnt_cnt]) # this is not supported in sonar right now

thread_2 = test_vector_0.add_thread()

output_list_cnt = output_lists_start * 64

for n in range(output_lists_start, output_lists_end):
    thread_2.wait_level("den == 1")

    for y in range(8):
        for x in range(8):
            thread_2.wait("assert(dout == $value)", output_array[output_list_cnt] - 128)
            output_list_cnt += 1
            thread_2.wait_posedge("clk")

thread_2.wait_flag(0)

# epilogue -----------------------------------------------------------------

# if there are many vectors, they can be selectively enabled by adding them
jpeg_tb.add_test_vector(test_vector_0)

# generate the output testbenches and data files for the specified languages
# at the designated path
jpeg_tb.generateTB(filepath, "sv")
