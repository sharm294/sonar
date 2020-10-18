"""
This module defines protocols on top of base interfaces for convenience
"""

from math import ceil

from .interfaces import AXIS


class Ethernet(object):
    """
    The Ethernet protocol over AXI-Stream
    """
    def __init__(self, mac_src, mac_dst, ether_type, prefix=None, suffix=None):
        """
        Initialize an Ethernet object

        Args:
            mac_src (str): Source MAC address e.g. '0xAABBCCDDEEFF'
            mac_dst (str): Destination MAC address e.g. '0xAABBCCDDEEFF'
            ether_type (str): Ether type e.g. '0x6677'
            prefix (str, optional): Defaults to None. Prefix data sent with file_to_stream
            suffix (str, optional): Defaults to None. Suffix data sent with file_to_stream
        """

        self.mac_src = mac_src
        self.mac_dst = mac_dst
        self.ether_type = ether_type
        self.prefix = prefix
        self.suffix = suffix

        self.header = self.mac_dst[2:] + self.mac_src[2:] + self.ether_type[2:]

    def file_to_stream(
        self, thread, interface, filepath, parsing_func=None, endian="little"
    ):
        """
        Stream the given file over the interface using the provided thread. The
        file is parsed using the parsing_func. By default, a binary file containing
        only data is assumed

        Args:
            thread (Thread): Thread to use to stream the file over
            interface (Interface): An instance of a Sonar interface such as AXIS
            filepath (str): Path to the file to stream
            parsing_func (Function, optional): Defaults to None. Function to parse
                the file with. This should return a list containing dicts
            endian (str, optional): Defaults to 'little'. Use 'little' or 'big'

        Raises:
            NotImplementedError: Unhandled exception
        """

        if parsing_func is None:
            parsing_func = interface._f2s_bin_data
        if filepath.endswith(".bin"):
            with open(filepath) as f:
                read_data = f.read()
                bin_data = bytearray(read_data)
                if self.prefix is not None:
                    bin_data[0:0] = bytearray.fromhex(self.prefix[2:])

                bin_data[0:0] = bytearray.fromhex(self.header)

                if self.suffix is not None:
                    bin_data.extend(bytearray.fromhex(self.suffix[2:]))
                interface._file_to_stream(thread, bin_data, parsing_func, endian)
        else:
            raise NotImplementedError()

    def bin_to_stream(
        self, thread, interface, bin_data, parsing_func=None, endian="little"
    ):
        """
        Stream the binary data over the interface using the provided thread. The
        file is parsed using the parsing_func.

        Args:
            thread (Thread): Thread to use to stream the file over
            interface (Interface): An instance of a Sonar interface such as AXIS
            bin_data (byteArray): Binary data to stream
            parsing_func (Function, optional): Defaults to None. Function to parse
                the file with. This should return a list containing dicts
            endian (str, optional): Defaults to 'little'. Use 'little' or 'big'

        Raises:
            NotImplementedError: Unhandled exception
        """

        if parsing_func is None:
            parsing_func = interface._f2s_bin_data
        if self.prefix is not None:
            bin_data[0:0] = bytearray.fromhex(self.prefix[2:])

        bin_data[0:0] = bytearray.fromhex(self.header)

        if self.suffix is not None:
            bin_data.extend(bytearray.fromhex(self.suffix[2:]))
        interface._file_to_stream(thread, bin_data, parsing_func, endian)

    def get_header_bytes(self):
        """
        Returns a bytearray representing the header (i.e. the ethernet headers
        and prefix, if there is one)

        Returns:
            byteArray: Represents the header
        """

        bin_array = bytearray.fromhex(self.header)

        if self.prefix is not None:
            bin_array.extend(bytearray.fromhex(self.prefix[2:]))

        return bin_array

    def wait_for_header(self, thread, interface, endian="little"):
        """
        Add a command to wait for the header in a testbench. The provided thread
        will wait on the Ethernet header to appear on the given interface

        Args:
            thread (Thread): Thread that will wait
            interface (Interface): An instance of a Sonar interface e.g. AXIS
            endian (str, optional): Defaults to 'little'. Use 'little' or 'big'

        Raises:
            NotImplementedError: Unhandled exception
        """

        octet = [0] * 14
        octet[0] = self.mac_dst[2:4]
        octet[1] = self.mac_dst[4:6]
        octet[2] = self.mac_dst[6:8]
        octet[3] = self.mac_dst[8:10]
        octet[4] = self.mac_dst[10:12]
        octet[5] = self.mac_dst[12:14]
        octet[6] = self.mac_src[2:4]
        octet[7] = self.mac_src[4:6]
        octet[8] = self.mac_src[6:8]
        octet[9] = self.mac_src[8:10]
        octet[10] = self.mac_src[10:12]
        octet[11] = self.mac_src[12:14]
        octet[12] = self.ether_type[2:4]
        octet[13] = self.ether_type[4:6]

        if isinstance(interface, AXIS):
            data_channel = "tdata"
        else:
            raise NotImplementedError
        data_width = interface.port.get_channel(data_channel)["size"] / 8
        wait_str = ""
        word_count = 0

        while word_count < ceil(14.0 / data_width):
            octet_count = word_count * data_width
            min_value = min(data_width, 14 - octet_count)
            word = "0x"
            if endian == "little":
                for i in range(min_value):
                    # upper_index = (((min_value - i)) * 8) - 1
                    # lower_index = (min_value - i - 1) * 8
                    octet_index = octet_count + min_value - i - 1
                    word += octet[octet_index]
                wait_str += (
                    interface.name
                    + "_"
                    + data_channel
                    + "["
                    + str(min_value * 8 - 1)
                    + ":0] == $value"
                )
            else:
                for i in range(min_value):
                    # upper_index = ((i + 1) * 8) - 1
                    # lower_index = i * 8
                    octet_index = octet_count + i
                    word += octet[octet_index]
                wait_str += (
                    interface.name
                    + "_"
                    + data_channel
                    + "["
                    + str(data_width * 8 - 1)
                    + ":"
                    + str((data_width - min_value) * 8)
                    + "] == $value"
                )
            thread.wait_level(wait_str, word)
            wait_str = ""
            word_count += 1
