"""
Defines the user interfaces for the available interfaces that can be used on 
modules in testbenches.
"""

from math import ceil
import math

from .base_types import SonarObject
from .base_types import InterfacePort


class AXIS(SonarObject):
    """
    Defines the AXI-Stream interface for master and slave
    """
    def __init__(self, name, direction, clock, flit=None, iClass=None):
        """
        Initializes an empty AXIS object

        Args:
            name (str): Name of the AXIS interface
            direction (str): master|slave
            clock (str): Associated clock signal

            flit (str, optional): Defaults to None. See below.
            iClass (str, optional): Defaults to None. See below
                flit and iClass are needed only for C++ simulation. They
                represent information about the stream objects used in HLS
                to define this AXIS interface. iClass is the name of the
                stream type and flit is a struct used in the iClass type:

                template<int D>
                struct simple_flit{
                    ap_uint<D> data;
                    ap_uint<1> last;
                };
                simple_flit<64> axis_word;
                typedef hls::stream<simple_flit<64> > axis_t;

                Here, axis_t would be the iClass and simple_flit<64> would be the
                flit.
        """

        self.name = name
        self.port = self._Port(name, direction, clock, flit, iClass)

    def write(self, thread, data, **kwargs):
        """
        Writes the given command to the AXI stream.

        Args:
            data (str): Data to write
            kwargs (str): keyworded arguments where the keyword is the AXIS
                channel or special keyword and is assigned to the given value
        Returns:
            dict: Dictionary representing the data transaction
        """
        payload_dict = self._payload(tdata=data, **kwargs)
        payload_arg = [payload_dict]
        self._write(thread, payload_arg)

    def writes(self, thread, data):
        """
        Writes an array of commands to the AXI stream. This command results in
        a smaller final file size than using the write command in a loop

        Args:
            thread (Thread): The thread to write the commands to
            data (Iterable): This should be an iterable of kwargs where the
                keywords are AXIS compliant.
        """

        payload_arg = []
        for datum in data:
            payload_dict = self._payload(**datum)
            payload_arg.append(payload_dict)

        self._write(thread, payload_arg)

    def _write(self, thread, payload):
        """
        Writes the given payload to the AXIS stream.

        Args:
            payload (list): Directly assigns a list containing valid
                transaction dicts to be written

        Returns:
            dict: Dictionary representing the data transaction
        """

        transaction = {
            "interface": {"type": "axis", "name": self.name, "iClass": self.port.iClass, "payload": payload}
        }
        thread._add_transaction(transaction)

    def _payload(self, existing_payload=None, **kwargs):
        """
        Formats the payload portion of an interface transaction

        Args:
            existing_payload (Dict, optional): Defaults to None. If an existing
                payload is being modified, pass it in. Otherwise an empty one is
                created
            kwargs: Keywords should be AXIS-compliant

        Returns:
            Dict: The new payload after the specified kwargs have been added
        """

        if existing_payload is None:
            payload_dict = {}
        else:
            payload_dict = existing_payload
        for key, value in kwargs.items():
            payload_dict[key] = value
        has_tkeep = False
        for channel in self.port.channels:
            if channel["type"] == "tdata":
                data_width = channel["size"]
            if channel["type"] == "tkeep":
                has_tkeep = True
        if has_tkeep and "tkeep" not in payload_dict:
            payload_dict["tkeep"] = 2**(int(data_width/8)) - 1

        return payload_dict

    def read(self, thread, data, **kwargs):
        """
        Reads the given keyworded args from an AXIS stream to verify output.

        Returns:
            dict: Dictionary representing the data transaction
        """

        self.write(thread, data, **kwargs)

    def reads(self, thread, data):
        """
        Reads the list of keyworded args from an AXI stream to verify output.
        This command results in a smaller file size than repeated 'read' commands.

        Args:
            thread (Thread): Thread to read the data in
            data (iterable): This should be an iterable of kwargs where the
                keywords are AXIS compliant.
        """

        self.writes(thread, data)

    def asdict(self):
        """
        Returns this object as a dictionary

        Returns:
            dict: The fields of this object as a dictionary
        """

        return self.port.asdict()

    def wait(self, thread, data, bit_range=None):
        """
        Adds a wait statement to the provided thread for a specific tdata value

        Args:
            thread (Thread): The thread to add the wait to
            data (number): The value of tdata to wait for
            bit_range (string, optional): Defaults to all bits. Range of bits
                to check in tdata, separated by a colon. e.g. "63:40"
        """

        if bit_range is None:
            wait_str = "(" + self.name + "_tdata == $value) "
        else:
            wait_str = self.name + "_tdata[" + bit_range + "] == $value)"

        wait_str += " && (" + self.name + "_tvalid == 1'b1)"
        if self.port.has_channel("tready"):
            wait_str += " && (" + self.name + "_tready == 1)"
        thread.wait_level(wait_str, data)

    def file_to_stream(self, thread, filepath, parsing_func=None, endian="little"):
        """
        Converts the provided file into a series of AXIS transactions.

        Args:
            thread (Thread): Thread to stream the file in
            filepath (str): Path to the file to stream
            parsing_func (Func, optional): Defaults to None. Function that
                determines how the file is parsed. Must return a list of dicts
                representing valid AXIS transactions. The default function
                assumes a binary file containing only tdata
            endian (str, optional): Defaults to 'little'. Must be little|big

        Raises:
            NotImplementedError: Unhandled exception

        Returns:
            dict: Dictionary representing the data transaction
        """

        transactions = []
        if parsing_func is None:
            parsing_func = self._f2s_bin_data
        if filepath.endswith(".bin"):
            with open(filepath) as f:
                transactions = parsing_func(f, endian)
        else:
            raise NotImplementedError()

        self._write(thread, transactions)

    def _file_to_stream(self, thread, open_file, parsing_func, endian):
        """
        Internal variant of file_to_stream where the file has already been
        opened, there are no optional arguments, and there is a return value

        Args:
            thread (Thread): Thread to stream the file in
            open_file (File): An opened file object
            parsing_func (Function): A function object to interpret the file with
            endian (str): 'little' or 'big'

        Returns:
            dict: Dictionary representing the data transaction
        """

        transactions = []
        transactions = parsing_func(open_file, endian)
        return self._write(thread, transactions)

    def _f2s_bin_data(self, data, endian):
        """
        A file parsing function for file_to_stream. Assumes a binary file that
        contains only tdata

        Args:
            data (file): Read data from the file
            endian (str): little|big

        Returns:
            list: Contains dicts representing each beat of AXIS transaction
        """

        transactions = []
        file_size = len(data)
        beat_count = (ceil(file_size / 8.0)) * 8
        beat = 0
        tdata_bytes = self.port.get_channel("tdata")["size"] / 8

        while beat < beat_count:
            tdata = 0
            for i in range(beat, beat + tdata_bytes):
                if endian == "little":
                    if i < file_size:
                        tdata = (tdata >> 8) | (data[i] << 56)
                    elif i < beat + tdata_bytes:
                        tdata = tdata >> 8
                else:  # big endian
                    if i < file_size:
                        tdata = (tdata << 8) | (data[i])
                    elif i < beat + tdata_bytes:
                        tdata = tdata << 8
            payload = self._payload(tdata="0x" + format(tdata, "08x"))

            if self.port.has_channel("tkeep"):
                tkeep = self._f2s_tkeep(file_size, tdata_bytes, beat, endian)
                payload = self._payload(payload, tkeep=tkeep)
            if self.port.has_channel("tlast"):
                tlast = self._f2s_tlast(file_size, beat)
                payload = self._payload(payload, tlast=tlast)

            transactions.append(payload)
            beat = beat + tdata_bytes

        return transactions

    @staticmethod
    def _f2s_tkeep(file_size, tdata_bytes, beat, endian):
        """
        Calculates tkeep for a particular beat for file_to_stream since the last
        beat may be smaller than a word.

        Args:
            file_size (int): Size of data in bytes to send over tdata
            tdata_bytes (int): Width of tdata in bytes
            beat (int): Beat counter
            endian (str): little|big

        Returns:
            str: Tkeep value for the current beat
        """

        if beat < ((ceil(file_size / 8.0) - 1) * 8.0):
            tkeep = "KEEP_ALL"
        else:
            size_last_transaction = file_size % tdata_bytes
            if size_last_transaction != 0:
                tkeep = ""
                for _ in range(size_last_transaction):
                    tkeep = tkeep + "1"
                if endian != "little":
                    for _ in range(tdata_bytes - size_last_transaction):
                        tkeep = tkeep + "0"
                tkeep = "0b" + tkeep
            else:
                tkeep = "KEEP_ALL"
        return tkeep

    @staticmethod
    def _f2s_tlast(file_size, beat):
        """
        Calculates tlast for a particular beat for file_to_stream. The last beat
        must assert tlast

        Args:
            file_size (int): Size of data in bytes to send over tdata
            beat (int): Beat counter

        Returns:
            str: Tlast value for the current beat
        """

        tlast = 0
        if beat >= ((ceil(file_size / 8.0) - 1) * 8):
            tlast = 1
        return tlast

    class _Port(InterfacePort):
        def __init__(self, name, direction, clock, flit, iClass):
            """
            Initializes an InterfacePort for AXI Stream

            Args:
                name (str): Name of the AXIS interface
                direction (str): slave|master
                clock (str): Name of associated clock
                flit (str): See below
                iClass (str): See below
                    See the docstring for AXIS.__init__(). These are used for
                    C++ simulation and represent the HLS stream
            """

            super(AXIS._Port, self).__init__(name, direction)
            self.type = "axis"
            self.clock = clock
            self.flit = flit
            self.connection_mode = "native"

            # this variable needs to be camelCase (i.e. no underscores) for RegEx
            self.iClass = iClass # pylint: disable=invalid-name

        def init_channels(self, mode, data_width=None, upper_case=True):
            """
            Initialize the channels associated with this AXIS interface. Initialize
            means to specify the names, types and widths of all the channels.

            Args:
                mode (str): Name of a channel preset to use. Options are:
                    'default': tdata, tvalid, tready, tlast
                    'tkeep': tdata, tvalid, tready, tlast, tkeep
                    'min': tdata, tvalid
                data_width (number): Width of the tdata field
                upper_case (bool, optional): Defaults to True. Assume that
                    the channel names are the uppercase versions of their type,
                    which is the default for an HLS module. Setting it to False
                    sets the name identical to the type (i.e. lowercase)

            Raises:
                NotImplementedError: Unhandled exception if bad mode entered
                ValueError: Error in mode/argument association
            """

            if mode == "default":
                if data_width is None:
                    print("data_width cannot be None")
                    raise ValueError
                channels = [
                    {"name": "tdata", "type": "tdata", "size": data_width},
                    {"name": "tvalid", "type": "tvalid"},
                    {"name": "tready", "type": "tready"},
                    {"name": "tlast", "type": "tlast"},
                ]
            elif mode == "tkeep":
                if data_width is None:
                    print("data_width cannot be None")
                    raise ValueError
                channels = [
                    {"name": "tdata", "type": "tdata", "size": data_width},
                    {"name": "tvalid", "type": "tvalid"},
                    {"name": "tready", "type": "tready"},
                    {"name": "tlast", "type": "tlast"},
                    {"name": "tkeep", "type": "tkeep", "size": data_width / 8},
                ]
            elif mode == "min":
                if data_width is None:
                    print("data_width cannot be None")
                    raise ValueError
                channels = [
                    {"name": "tdata", "type": "tdata", "size": data_width},
                    {"name": "tvalid", "type": "tvalid"},
                ]
            elif mode == "empty":
                channels = []
            else:
                raise NotImplementedError()
            for channel in channels:
                if upper_case:
                    channel["name"] = channel["name"].upper()
            self.add_channels(channels)

        def asdict(self):
            """
            Returns this object as a dictionary

            Returns:
                dict: The fields of this object as a dictionary
            """
            port = super(AXIS._Port, self).asdict()
            port["type"] = self.type
            port["clock"] = self.clock
            if self.flit is not None:
                port["flit"] = self.flit
            if self.iClass is not None:
                port["iClass"] = self.iClass
            port["connection_mode"] = self.connection_mode
            return port


class SAXILite(SonarObject):
    """
    Defines the AXI-Lite slave interface
    """
    def __init__(self, name, clock, reset):
        """
        Initialize an SAXILite interface with the default options

        Args:
            name (str): Name of the AXI4-Lite interface
            clock (str): Name of associated clock
            reset (str): Name of associated reset
        """

        self.name = name
        self.port = self._Port(name, clock, reset)

    def set_address(self, addr_range, addr_offset):
        """
        Sets the address range and offset for this AXI-Lite interface

        Args:
            addr_range (str): Address size e.g. '4K'
            addr_offset (number): Offset address
        """

        self.port.set_address(addr_range, addr_offset)

    def add_register(self, name, address):
        """
        Add a register to this interface

        Args:
            name (str): Name of the register to add
            address (number): Address of the register
        """

        self.port.add_register(name, address)

    def del_register(self, name):
        """
        Delete a register from this interface

        Args:
            name (str): Name of the register to delete
        """

        self.port.del_register(name)

    def write(self, thread, register, data):
        """
        Write data to a register

        Args:
            thread (Thread): Thread in which to write from
            register (str): Name of the register to write to
            data (number): Value that should be written
        """

        address = None
        for index, reg in enumerate(self.port.registers):
            if reg == register:
                address = self.port.addresses[index]
                break
        transaction = {
            "interface": {
                "type": "s_axilite",
                "name": self.name,
                "payload": [{"mode": 1, "data": data, "addr": address}],
            }
        }
        thread._add_transaction(transaction)

    def read(self, thread, register, expected_value):
        """
        Read data from a register to verify its value

        Args:
            thread (Thread): Thread in which to read from
            register (str): Name of the register to read
            expected_value (number): Expected value that the register should have
        """

        address = None
        for index, reg in enumerate(self.port.registers):
            if reg == register:
                address = self.port.addresses[index]
                break
        transaction = {
            "interface": {
                "type": "s_axilite",
                "name": self.name,
                "payload": [{"mode": 0, "data": expected_value, "addr": address}],
            }
        }
        thread._add_transaction(transaction)

    def asdict(self):
        """
        Returns this object as a dictionary

        Returns:
            dict: The fields of this object as a dictionary
        """

        return self.port.asdict()

    class _Port(InterfacePort):
        def __init__(self, name, clock, reset):
            """
            Initialize an interface port for AXILite

            Args:
                name (str): Name of the interface port
                clock (str): Name of associated clock
                reset (str): Name of associated reset
            """

            super(SAXILite._Port, self).__init__(name, "mixed")
            self.type = "s_axilite"
            self.clock = clock
            self.reset = reset
            self.connection_mode = "ip"
            self.registers = []
            self.addresses = []
            self.addr_range = ""
            self.addr_offset = ""

            # these variables can't have underscores for RegEx
            self.dataWidth = 0 # pylint: disable=invalid-name
            self.addrWidth = 0 # pylint: disable=invalid-name

        def set_address(self, addr_range, addr_offset):
            """
            Sets the address range and offset for this AXI-Lite interface

            Args:
                addr_range (str): Address size e.g. '4K'
                addr_offset (number): Offset address
            """

            self.addr_range = addr_range
            self.addr_offset = addr_offset

        def add_register(self, name, address):
            """
            Add a register to this interface

            Args:
                name (str): Name of the register to add
                address (number): Address of the register
            """

            self.registers.append(name)
            self.addresses.append(address)

        def del_register(self, name):
            """
            Delete a register from this interface

            Args:
                name (str): Name of the register to delete
            """

            for index, name_ in enumerate(self.registers):
                if name_ == name:
                    del self.registers[index]
                    del self.addresses[index]
                    break

        def init_channels(
            self, mode, data_width=None, addr_width=None, upper_case=True
        ):
            """
            Initialize the channels associated with this AXILite interface.
            Initialize means to specify the names, types and widths of all the
            channels.

            Args:
                mode (str): Name of a channel preset to use. Options are:
                    'default': standard AXI-Lite without cache or prot
                data_width (number): Width of the data channel (r/w)
                addr_width (number): Width of the addr channel (r/w)
                upper_case (bool, optional): Defaults to True. Assume that
                    the channel names are the uppercase versions of their type,
                    which is the default for an HLS module. Setting it to False
                    sets the name identical to the type (i.e. lowercase)

            Raises:
                NotImplementedError: Unhandled exception if bad mode entered
                ValueError: Error in mode/argument association
            """
            if mode == "default":
                if data_width is None or addr_width is None:
                    print("data_width or addr_width cannot be None")
                    raise ValueError
                if addr_width < 12:
                    addr_width = 12 # Required by AXI standard for 4K memory
                channels = [
                    {"name": "awvalid", "type": "awvalid"},
                    {"name": "awready", "type": "awready"},
                    {"name": "awaddr", "type": "awaddr", "size": addr_width},
                    {"name": "wvalid", "type": "wvalid"},
                    {"name": "wready", "type": "wready"},
                    {"name": "wdata", "type": "wdata", "size": data_width},
                    {"name": "wstrb", "type": "wstrb", "size": int(data_width / 8)},
                    {"name": "arvalid", "type": "arvalid"},
                    {"name": "arready", "type": "arready"},
                    {"name": "araddr", "type": "araddr", "size": addr_width},
                    {"name": "rvalid", "type": "rvalid"},
                    {"name": "rready", "type": "rready"},
                    {"name": "rdata", "type": "rdata", "size": data_width},
                    {"name": "rresp", "type": "rresp", "size": 2},
                    {"name": "bvalid", "type": "bvalid"},
                    {"name": "bready", "type": "bready"},
                    {"name": "bresp", "type": "bresp", "size": 2},
                ]
                self.dataWidth = data_width
                self.addrWidth = addr_width
            elif mode == "empty":
                channels = []
            else:
                raise NotImplementedError
            for channel in channels:
                if upper_case:
                    channel["name"] = channel["name"].upper()
            self.add_channels(channels)

        def asdict(self):
            """
            Returns this object as a dictionary

            Returns:
                dict: The fields of this object as a dictionary
            """
            port = port = super(SAXILite._Port, self).asdict()
            port["type"] = self.type
            port["clock"] = self.clock
            port["reset"] = self.reset
            port["registers"] = self.registers
            port["addresses"] = self.addresses
            port["addr_offset"] = self.addr_offset
            port["addr_range"] = self.addr_range
            port["connection_mode"] = self.connection_mode
            port["data_width"] = self.dataWidth

            port["readResp"] = "rresp_" + str(self.index)
            port["writeResp"] = "wresp_" + str(self.index)
            port["readData"] = "rdata_" + str(self.index)
            port["agent"] = "master_agent_" + str(self.index)
            return port
