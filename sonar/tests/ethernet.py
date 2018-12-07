import os

from sonar.sonar import Thread
from sonar.generators import EthernetAXIS

def ethernet():

    test_file_name = "test_axis.bin"

    #writing random garbage data to test.txt
    with open(test_file_name, "wb") as binary_file:
        num_bytes_written = binary_file.write(b'\xDE\xAD\xBE\xEF\xFA\xCE\xFA\xCE')
        num_bytes_written = binary_file.write(b'\x11\x22\x33\x44\x55\x66\x77\x88')
        num_bytes_written = binary_file.write(b'\x00\xaa\xbb\xcc\xdd\xee\xff\x12')
        num_bytes_written = binary_file.write(b'\x34\x56\x78')
    
    thread = Thread() # create empty thread
    ethernet = EthernetAXIS("axis_in", 'master', 'clock', "0xAABBCCDDEEFF", 
        "0x001122334455", "0x6677")

    # initialize with tkeep profile containing data, last, ready, tkeep, valid
    ethernet.port.init_channels('tkeep', 64, False)
    ethernet.prefix = '0x0011'
    ethernet.file_to_stream(thread, test_file_name, endian='little')

    ethernet.wait_for_header(thread, 'little')

    print(thread)

    os.remove(test_file_name)

if __name__ == "__main__":
    ethernet()