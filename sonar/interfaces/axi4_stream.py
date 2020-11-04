"""
Defines an AXI4-Stream interface
"""

from math import ceil

import sonar.base_types
import sonar.interfaces.base_interface as base


class AXI4Stream(base.BaseInterface):
    """
    Defines the AXI-Stream interface for master and slave
    """

    def __init__(self, name, direction, clock, flit=None, iClass=None):
        """
        Initializes an empty AXI4Stream object

        Args:
            name (str): Name of the AXI4Stream interface
            direction (str): master|slave
            clock (str): Associated clock signal
            data_width (int): Width of tdata

            flit (str, optional): Defaults to None. See below.
            iClass (str, optional): Defaults to None. See below
                flit and iClass are needed only for C++ simulation. They
                represent information about the stream objects used in HLS
                to define this AXI4Stream interface. iClass is the name of the
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

        super().__init__(name, direction, AXI4StreamCore)
        self.clock = clock
        self.flit = flit
        self.interface_type = "axi4_stream"

        # this variable needs to be camelCase (i.e. no underscores) for RegEx
        self.iClass = iClass  # pylint: disable=invalid-name

    def init_signals(self, mode, data_width, upper_case=True):
        """
        Initialize the signals associated with this AXI4Stream interface. Initialize
        means to specify the names, types and widths of all the signals.

        Args:
            mode (str): Name of a signal preset to use. Options are:
                'default': tdata, tvalid, tready, tlast
                'tkeep': tdata, tvalid, tready, tlast, tkeep
                'min': tdata, tvalid
            data_width (number): Width of the tdata field
            upper_case (bool, optional): Defaults to True. Assume that
                the signal names are the uppercase versions of their type,
                which is the default for an HLS module. Setting it to False
                sets the name identical to the type (i.e. lowercase)
        """

        if mode == "default":
            signals = {
                "tdata": sonar.base_types.Signal("tdata", data_width),
                "tvalid": sonar.base_types.Signal("tvalid", 1),
                "tready": sonar.base_types.Signal("tready", 1),
                "tlast": sonar.base_types.Signal("tlast", 1),
            }
        elif mode == "tkeep":
            signals = {
                "tdata": sonar.base_types.Signal("tdata", data_width),
                "tvalid": sonar.base_types.Signal("tvalid", 1),
                "tready": sonar.base_types.Signal("tready", 1),
                "tlast": sonar.base_types.Signal("tlast", 1),
                "tkeep": sonar.base_types.Signal("tkeep", data_width / 8),
            }
        elif mode == "min":
            signals = {
                "tdata": sonar.base_types.Signal("tdata", data_width),
                "tvalid": sonar.base_types.Signal("tvalid", 1),
            }
        if upper_case:
            signals = base.to_upper_case(signals)
        self.add_signals(signals)

    def write(self, thread, data, **kwargs):
        """
        Writes the given command to the AXI stream.

        Args:
            data (str): Data to write
            kwargs (str): keyworded arguments where the keyword is the AXI4Stream
                signal or special keyword and is assigned to the given value
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
                keywords are AXI4Stream compliant.
        """

        payload_arg = []
        for datum in data:
            payload_dict = self._payload(**datum)
            payload_arg.append(payload_dict)

        self._write(thread, payload_arg)

    def _write(self, thread, payload):
        """
        Writes the given payload to the AXI4Stream stream.

        Args:
            payload (list): Directly assigns a list containing valid
                transaction dicts to be written

        Returns:
            dict: Dictionary representing the data transaction
        """

        transaction = {
            "interface": {
                "type": "axi4_stream",
                "name": self.name,
                "iClass": self.iClass,
                "payload": payload,
            }
        }
        thread._add_transaction(transaction)

    def _payload(self, existing_payload=None, **kwargs):
        """
        Formats the payload portion of an interface transaction

        Args:
            existing_payload (Dict, optional): Defaults to None. If an existing
                payload is being modified, pass it in. Otherwise an empty one is
                created
            kwargs: Keywords should be AXI4Stream-compliant

        Returns:
            Dict: The new payload after the specified kwargs have been added
        """

        if existing_payload is None:
            payload_dict = {}
        else:
            payload_dict = existing_payload
        for key, value in kwargs.items():
            payload_dict[key] = value
        if self.has_signal("tkeep") and "tkeep" not in payload_dict:
            data_width = self.signals["tdata"].size
            payload_dict["tkeep"] = 2 ** (int(data_width / 8)) - 1
        if self.has_signal("tlast") and "tlast" not in payload_dict:
            payload_dict["tlast"] = 0
        if self.has_signal("tdest") and "tdest" not in payload_dict:
            payload_dict["tdest"] = 0
        return payload_dict

    def read(self, thread, data, **kwargs):
        """
        Reads the given keyworded args from an AXI4Stream stream to verify output.

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
                keywords are AXI4Stream compliant.
        """

        self.writes(thread, data)

    def asdict(self):
        """
        Returns this object as a dictionary

        Returns:
            dict: The fields of this object as a dictionary
        """

        tmp = super().asdict()
        tmp["clock"] = self.clock
        if self.flit is not None:
            tmp["flit"] = self.flit
        if self.iClass is not None:
            tmp["iClass"] = self.iClass
        tmp["connection_mode"] = self.connection_mode
        return tmp

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
        if self.has_signal("tready"):
            wait_str += " && (" + self.name + "_tready == 1)"
        thread.wait_level(wait_str, data)

    def file_to_stream(
        self, thread, filepath, parsing_func=None, endian="little"
    ):
        """
        Converts the provided file into a series of AXI4Stream transactions.

        Args:
            thread (Thread): Thread to stream the file in
            filepath (str): Path to the file to stream
            parsing_func (Func, optional): Defaults to None. Function that
                determines how the file is parsed. Must return a list of dicts
                representing valid AXI4Stream transactions. The default function
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
            list: Contains dicts representing each beat of AXI4Stream transaction
        """

        transactions = []
        file_size = len(data)
        beat_count = (ceil(file_size / 8.0)) * 8
        beat = 0
        tdata_bytes = self.get_signal("tdata").size / 8

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

            if self.has_signal("tkeep"):
                tkeep = self._f2s_tkeep(file_size, tdata_bytes, beat, endian)
                payload = self._payload(payload, tkeep=tkeep)
            if self.has_signal("tlast"):
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


class AXI4StreamCore(base.InterfaceCore):
    """
    Defines the core properties of the AXI4-Stream interface used internally
    """

    signals = {
        "input": {"tready": {"size": 1, "required": False}},
        "output": {
            "tdata": {"size": 0, "required": True},
            "tvalid": {"size": 1, "required": True},
            "tlast": {"size": 1, "required": False},
            "tkeep": {"size": 0, "required": False},
            "tdest": {"size": 0, "required": False},
            "tid": {"size": 0, "required": False},
            "tuser": {"size": 0, "required": False},
        },
    }

    actions = {
        "sv": {
            "master": [
                "wait($$clock == 0);",
                {
                    "signals": {"tdata", "tlast", "tkeep", "tdest"},
                    "commands": ["$$name_$$signal = args[$$i];"],
                },
                "$$name_tvalid = 1'b1;",
                "@(posedge $$clock iff $$name_tready === 1'b1);",
                "@(negedge $$clock);",
                "$$name_tvalid = 1'b0;",
            ],
            "slave": [
                "@(posedge $$clock iff $$name_tready && $$name_tvalid);",
                {
                    "signals": {"tdata", "tlast", "tkeep", "tdest"},
                    "commands": [
                        "assert($$name_$$signal == args[$$i]) begin\n"
                        "end else begin\n"
                        '    $error("AXI-S Assert failed at %t on $$name_$$signal. Expected: %h, Received: %h", $time, args[$$i], $$name_$$signal);\n'
                        "    error = 1'b1;\n"
                        "    $stop;\n"
                        "end"
                    ],
                },
            ],
        },
        "cpp": {
            "master": [
                {
                    "signals": {"tdata", "tlast", "tkeep", "tdest"},
                    "commands": ["$$name_flit.$$signal = args[$$i];"],
                },
                "$$name.write($$name_flit);",
            ],
            "slave": [
                "$$name.read($$name_flit);",
                {
                    "signals": {"tdata", "tlast", "tkeep", "tdest"},
                    "commands": [
                        'assert($$name_flit.$$signal == args[$$i] && "Assert failed on $$name_flit.$$signal");'
                    ],
                },
            ],
        },
    }

    args = {
        "sv": {"tdata": 0, "tlast": 1, "tkeep": 2, "tdest": 3},
        "cpp": {"tdata": 0, "tlast": 1, "tkeep": 2, "tdest": 3},
    }

    @classmethod
    def write_cpp(cls, packet, identifier="NULL"):
        """
        Write one line of the C++ data file

        Args:
            packet (dict): The command to write

        Returns:
            str: The command as a line for the data file
        """
        return super().write_cpp(packet, str(packet["iClass"]))
