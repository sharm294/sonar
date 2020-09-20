import os
import random

from sonar.testbench import Testbench, Module, TestVector

# from sonar.interfaces import AXIS, SAXILite


# create top-level entity for the testbench using the default constructor
# and set the Module_Name metadata tag to 'sample' as specified by the
# default constructor.
adder_tb = Testbench.default("adder")
filepath = os.path.join(os.path.dirname(__file__), "build/")

# the DUT ------------------------------------------------------------------

# create a DUT module named 'DUT' and specify its signal ports
dut = Module.default("DUT")
dut.add_port("A", "input", 4)
dut.add_port("B", "input", 4)
dut.add_port("X", "output", 4)

adder_tb.add_module(dut)

# test vectors -------------------------------------------------------------


def test_adder(test_vector, a, b):
    thread_0 = test_vector.add_thread()
    thread_0.set_signal("A", a)
    thread_0.set_signal("B", b)
    thread_0.add_delay("2ns")
    thread_0.wait("assert(X == $value)", a + b)
    thread_0.end_vector()  # terminates the test vector


test_vector_0 = TestVector()
test_adder(test_vector_0, 5, 10)

test_vector_1 = TestVector()
a = random.randint(0, 15)  # nosec
b = random.randint(0, 15)  # nosec
test_adder(test_vector_0, a, b)

# epilogue -----------------------------------------------------------------

# if there are many vectors, they can be selectively enabled by adding them
adder_tb.add_test_vector(test_vector_0)
adder_tb.add_test_vector(test_vector_1)

# generate the output testbenches and data files for the specified languages
# at the designated path
adder_tb.generateTB(filepath, "sv")
