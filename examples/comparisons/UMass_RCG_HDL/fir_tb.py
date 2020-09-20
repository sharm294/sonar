import os

from sonar.testbench import Testbench, Module, TestVector


# create top-level entity for the testbench using the default constructor
# and set the Module_Name metadata tag to 'sample' as specified by the
# default constructor.
fir_tb = Testbench.default("fir_filter")
filepath = os.path.join(os.path.dirname(__file__), "build/")

# the DUT ------------------------------------------------------------------

# create a DUT module named 'DUT' and specify its signal ports
dut = Module.default("DUT")
dut.add_clock_port("clk", "20ns")
dut.add_reset_port("reset")
dut.add_port("data_in_msb", size=1, direction="input")
dut.add_port("data_in_lsb", size=7, direction="input")
dut.add_port("load_c", direction="input")
for i in range(8):
    dut.add_port(f"coef_in_{i}", direction="input")
for i in range(18):
    dut.add_port(f"data_out_{i}", direction="output")
dut.add_parameter("TAPS", 25)

fir_tb.add_module(dut)

# test vectors -------------------------------------------------------------

test_vector_0 = TestVector()


def delayed_set(thread, delay, signal, value):
    if isinstance(delay, (int, float)):
        delay = str(delay) + "ns"
    thread.add_delay(delay)
    thread.set_signal(signal, value)


def toggle_set(thread, delay_0, delay_1, signal):
    delayed_set(thread, delay_0, signal, 1)
    delayed_set(thread, delay_1, signal, 0)


def delayed_assert(thread, delay, signal, value):
    if isinstance(delay, (int, float)):
        delay = str(delay) + "ns"
    thread.add_delay(delay)
    thread.wait(f"assert({signal} == $value)", value)


def toggle_assert(thread, delay_0, delay_1, signal):
    delayed_assert(thread, delay_0, signal, 1)
    delayed_assert(thread, delay_1, signal, 0)


thread_0 = test_vector_0.add_thread()
thread_0.init_signals()
thread_0.set_signal("load_c", 1)
thread_0.set_signal("data_in_lsb", 0x40)
thread_0.add_delay("500ns")
thread_0.set_signal("load_c", 0)

thread_1 = test_vector_0.add_thread()
toggle_set(thread_1, "300ns", "200ns", "coef_in_4")

thread_2 = test_vector_0.add_thread()
toggle_set(thread_2, 140, 160, "coef_in_3")
toggle_set(thread_2, 160, 40, "coef_in_3")
# thread_2.add_delay("140ns")
# thread_2.set_signal("coef_in_3", 1)
# thread_2.add_delay("160ns")
# thread_2.set_signal("coef_in_3", 0)
# thread_2.add_delay("160ns")
# thread_2.set_signal("coef_in_3", 1)
# thread_2.add_delay("40ns")
# thread_2.set_signal("coef_in_3", 0)

thread_3 = test_vector_0.add_thread()
thread_3.add_delay("60ns")
for i in range(2):
    toggle_set(thread_3, 80, 80, "coef_in_2")
    # thread_3.set_signal("coef_in_2", 1)
    # thread_3.add_delay("80ns")
    # thread_3.set_signal("coef_in_2", 0)
    # thread_3.add_delay("80ns")
thread_3.set_signal("coef_in_2", 1)
# thread_3.add_delay("80ns")
# thread_3.set_signal("coef_in_2", 0)
delayed_set(thread_3, 80, "coef_in_2", 0)

thread_4 = test_vector_0.add_thread()
thread_4.add_delay("20ns")
# for i in range(5):
# thread_4.set_signal("coef_in_1", 1)
# thread_4.add_delay("40ns")
# thread_4.set_signal("coef_in_1", 0)
# thread_4.add_delay("40ns")

thread_4.set_signal("coef_in_1", 1)
thread_4.add_delay("40ns")
thread_4.set_signal("coef_in_1", 0)

thread_5 = test_vector_0.add_thread()
thread_5.add_delay("1ns")  # offset from thread 0 a bit
for i in range(12):
    thread_5.set_signal("coef_in_0", 1)
    thread_5.add_delay("20ns")
    thread_5.set_signal("coef_in_0", 0)
    thread_5.add_delay("20ns")
thread_5.set_signal("coef_in_0", 1)
thread_5.add_delay("20ns")
thread_5.set_signal("coef_in_0", 0)

thread_6 = test_vector_0.add_thread()
thread_6.add_delay("500ns")
thread_6.set_signal("data_in_msb", 1)
thread_6.add_delay("500ns")
thread_6.set_signal("data_in_msb", 0)
thread_6.add_delay("495ns")
thread_6.set_signal("data_in_msb", 1)
thread_6.add_delay("500ns")
thread_6.set_signal("data_in_msb", 0)
thread_6.add_delay("490ns")
thread_6.set_signal("data_in_msb", 1)
thread_6.add_delay("500ns")
thread_6.set_signal("data_in_msb", 0)
thread_6.add_delay("495ns")
thread_6.set_signal("data_in_msb", 1)
thread_6.add_delay("500ns")
thread_6.set_signal("data_in_msb", 0)

thread_7 = test_vector_0.add_thread()
for i in range(18):
    thread_7.wait(f"assert(data_out_{i} == $value)", 0)

thread_8 = test_vector_0.add_thread()
toggle_assert(thread_8, 737.787, 580, "data_out_15")
toggle_assert(thread_8, 340, 660, "data_out_15")
toggle_assert(thread_8, 320, 660, "data_out_15")
delayed_assert(thread_8, 340, "data_out_15", 1)

thread_9 = test_vector_0.add_thread()
toggle_assert(thread_9, 657.781, 80, "data_out_14")
toggle_assert(thread_9, 120, 320, "data_out_14")
toggle_assert(thread_9, 140, 340, "data_out_14")
toggle_assert(thread_9, 160, 360, "data_out_14")
toggle_assert(thread_9, 140, 320, "data_out_14")
toggle_assert(thread_9, 160, 360, "data_out_14")
toggle_assert(thread_9, 140, 340, "data_out_14")
delayed_assert(thread_9, 160, "data_out_14", 1)

thread_10 = test_vector_0.add_thread()
toggle_assert(thread_10, 617.549, 40, "data_out_13")
toggle_assert(thread_10, 40, 40, "data_out_13")
toggle_assert(thread_10, 60, 60, "data_out_13")
toggle_assert(thread_10, 100, 160, "data_out_13")
toggle_assert(thread_10, 60, 60, "data_out_13")
toggle_assert(thread_10, 80, 120, "data_out_13")
toggle_assert(thread_10, 180, 40, "data_out_13")
toggle_assert(thread_10, 80, 80, "data_out_13")
toggle_assert(thread_10, 100, 200, "data_out_13")
toggle_assert(thread_10, 60, 60, "data_out_13")
toggle_assert(thread_10, 80, 120, "data_out_13")
toggle_assert(thread_10, 160, 40, "data_out_13")
toggle_assert(thread_10, 80, 80, "data_out_13")
toggle_assert(thread_10, 100, 200, "data_out_13")
toggle_assert(thread_10, 60, 60, "data_out_13")
toggle_assert(thread_10, 80, 120, "data_out_13")
toggle_assert(thread_10, 180, 40, "data_out_13")
toggle_assert(thread_10, 80, 80, "data_out_13")
delayed_assert(thread_9, 100, "data_out_13", 1)

thread_11 = test_vector_0.add_thread()
thread_11.add_delay("597.777ns")
for i in range(3):
    thread_11.wait("assert(data_out_12 == $value)", 1)
    delayed_assert(thread_11, 20, "data_out_12", 0)
    thread_11.add_delay("20ns")
for i in range(3):
    thread_11.wait("assert(data_out_12 == $value)", 1)
    delayed_assert(thread_11, 20, "data_out_12", 0)
    thread_11.add_delay("40ns")
thread_11.wait("assert(data_out_12 == $value)", 1)
delayed_assert(thread_11, 60, "data_out_12", 0)
toggle_assert(thread_11, 80, 60, "data_out_12")
toggle_assert(thread_11, 20, 20, "data_out_12")
toggle_assert(thread_11, 40, 40, "data_out_12")
toggle_assert(thread_11, 20, 40, "data_out_12")
toggle_assert(thread_11, 40, 60, "data_out_12")
toggle_assert(thread_11, 60, 180, "data_out_12")
delayed_assert(thread_11, 20, "data_out_12", 1)
thread_11.add_delay("20ns")
for i in range(2):
    thread_11.wait("assert(data_out_12 == $value)", 0)
    delayed_assert(thread_11, 40, "data_out_12", 1)
    thread_11.add_delay("40ns")
thread_11.wait("assert(data_out_12 == $value)", 0)
toggle_assert(thread_11, 40, 60, "data_out_12")
toggle_assert(thread_11, 100, 80, "data_out_12")
toggle_assert(thread_11, 20, 20, "data_out_12")
toggle_assert(thread_11, 40, 40, "data_out_12")
toggle_assert(thread_11, 20, 40, "data_out_12")
toggle_assert(thread_11, 40, 60, "data_out_12")
toggle_assert(thread_11, 60, 160, "data_out_12")
delayed_assert(thread_11, 20, "data_out_12", 1)
thread_11.add_delay("20ns")
for i in range(2):
    thread_11.wait("assert(data_out_12 == $value)", 0)
    delayed_assert(thread_11, 40, "data_out_12", 1)
    thread_11.add_delay("40ns")
thread_11.wait("assert(data_out_12 == $value)", 0)
toggle_assert(thread_11, 40, 60, "data_out_12")
toggle_assert(thread_11, 100, 80, "data_out_12")
toggle_assert(thread_11, 20, 20, "data_out_12")
toggle_assert(thread_11, 40, 40, "data_out_12")
toggle_assert(thread_11, 20, 40, "data_out_12")
toggle_assert(thread_11, 40, 60, "data_out_12")
toggle_assert(thread_11, 60, 180, "data_out_12")
delayed_assert(thread_11, 20, "data_out_12", 1)
thread_11.add_delay("20ns")
for i in range(2):
    thread_11.wait("assert(data_out_12 == $value)", 0)
    delayed_assert(thread_11, 40, "data_out_12", 1)
    thread_11.add_delay("40ns")
thread_11.wait("assert(data_out_12 == $value)", 0)
toggle_assert(thread_11, 40, 60, "data_out_12")
delayed_assert(thread_11, 100, "data_out_12", 1)

thread_12 = test_vector_0.add_thread()
thread_12.add_delay("757.555ns")
for i in range(2):
    thread_12.wait("assert(data_out_11 == $value)", 1)
    delayed_assert(thread_12, 40, "data_out_11", 0)
    thread_12.add_delay("20ns")
thread_12.wait("assert(data_out_11 == $value)", 1)
delayed_assert(thread_12, 20, "data_out_11", 0)
toggle_assert(thread_12, 20, 40, "data_out_11")
toggle_assert(thread_12, 20, 60, "data_out_11")
toggle_assert(thread_12, 80, 40, "data_out_11")
toggle_assert(thread_12, 20, 20, "data_out_11")
thread_12.add_delay("40ns")
for i in range(2):
    thread_12.wait("assert(data_out_11 == $value)", 1)
    delayed_assert(thread_12, 20, "data_out_11", 0)
    thread_12.add_delay("20ns")
thread_12.wait("assert(data_out_11 == $value)", 1)
delayed_assert(thread_12, 40, "data_out_11", 0)
toggle_assert(thread_12, 20, 20, "data_out_11")
toggle_assert(thread_12, 40, 60, "data_out_11")
toggle_assert(thread_12, 100, 40, "data_out_11")
thread_12.add_delay("40ns")
for i in range(5):
    thread_12.wait("assert(data_out_11 == $value)", 1)
    delayed_assert(thread_12, 20, "data_out_11", 0)
    thread_12.add_delay("20ns")
thread_12.wait("assert(data_out_11 == $value)", 1)
delayed_assert(thread_12, 40, "data_out_11", 0)
toggle_assert(thread_12, 40, 60, "data_out_11")
toggle_assert(thread_12, 100, 40, "data_out_11")
toggle_assert(thread_12, 20, 20, "data_out_11")
thread_12.add_delay("40ns")
for i in range(2):
    thread_12.wait("assert(data_out_11 == $value)", 1)
    delayed_assert(thread_12, 20, "data_out_11", 0)
    thread_12.add_delay("20ns")
thread_12.wait("assert(data_out_11 == $value)", 1)
delayed_assert(thread_12, 40, "data_out_11", 0)
toggle_assert(thread_12, 20, 20, "data_out_11")
toggle_assert(thread_12, 40, 60, "data_out_11")
toggle_assert(thread_12, 80, 40, "data_out_11")
thread_12.add_delay("40ns")
for i in range(5):
    thread_12.wait("assert(data_out_11 == $value)", 1)
    delayed_assert(thread_12, 20, "data_out_11", 0)
    thread_12.add_delay("20ns")
thread_12.wait("assert(data_out_11 == $value)", 1)
delayed_assert(thread_12, 40, "data_out_11", 0)
toggle_assert(thread_12, 40, 60, "data_out_11")
toggle_assert(thread_12, 100, 40, "data_out_11")
toggle_assert(thread_12, 20, 20, "data_out_11")
thread_12.add_delay("40ns")
for i in range(2):
    thread_12.wait("assert(data_out_11 == $value)", 1)
    delayed_assert(thread_12, 20, "data_out_11", 0)
    thread_12.add_delay("20ns")
thread_12.wait("assert(data_out_11 == $value)", 1)
delayed_assert(thread_12, 40, "data_out_11", 0)
toggle_assert(thread_12, 20, 20, "data_out_11")
toggle_assert(thread_12, 40, 60, "data_out_11")
toggle_assert(thread_12, 100, 40, "data_out_11")
thread_12.add_delay("40ns")
for i in range(5):
    thread_12.wait("assert(data_out_11 == $value)", 1)
    delayed_assert(thread_12, 20, "data_out_11", 0)
    thread_12.add_delay("20ns")
thread_12.wait("assert(data_out_11 == $value)", 1)
delayed_assert(thread_12, 40, "data_out_11", 0)
toggle_assert(thread_12, 40, 60, "data_out_11")

outputT.end_vector()  # terminates the test vector

# epilogue -----------------------------------------------------------------

# if there are many vectors, they can be selectively enabled by adding them
fir_tb.add_test_vector(test_vector_0)

# generate the output testbenches and data files for the specified languages
# at the designated path
fir_tb.generateTB(filepath, "sv")
