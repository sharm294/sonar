from math import ceil

from .base_types import SonarObject
from .base_types import InterfacePort

class AXIS(SonarObject):

    def __init__(self, name, direction, clock, c_struct=None, c_stream=None):
        """
        Initializes an empty AXIS object
        
        Args:
            name (str): Name of the AXIS interface
            direction (str): master|slave
            clock (str): Associated clock signal

            c_struct (str, optional): Defaults to None. See below.
            c_stream (str, optional): Defaults to None. See below
                c_struct and c_stream are needed only for C++ simulation. They
                represent information about the hls::stream objects used in HLS 
                to define this AXIS interface. c_stream is the name of the 
                struct itself and c_struct is a variable of the c_stream type:

                template<int D>
                struct uaxis_l{ <--------------------- uaxis_l would be c_stream
                    ap_uint<D> data;
                    ap_uint<1> last;
                };
                uaxis_l<64> axis_word; <------------ axis_word would be c_struct
                typedef hls::stream<uaxis_l<64> > axis_t;
        """

        self.name = name
        self.port = self._Port(name, direction, clock, c_struct, c_stream)

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
        payloadDict = self._payload(tdata=data, **kwargs)
        payloadArg = [payloadDict]
        self._write(thread, payloadArg)

    def writes(self, thread, data):
        """
        Writes an array of commands to the AXI stream. This command results in
        a smaller final file size than using the write command in a loop
        
        Args:
            thread (Thread): The thread to write the commands to
            data (Iterable): This should be an iterable of kwargs where the 
                keywords are AXIS compliant.
        """

        payloadArg = []
        for datum in data:
            payloadDict = self._payload(**datum)
            payloadArg.append(payloadDict)
        
        self._write(thread, payloadArg)
    
    def _write(self, thread, payload):
        """
        Writes the given payload to the AXIS stream.

        Args:
            payload (list): Directly assigns a list containing valid 
                transaction dicts to be written

        Returns:
            dict: Dictionary representing the data transaction
        """

        transaction = {'interface': {
            'type': 'axis','name': self.name, 'payload': payload
        }}
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
            payloadDict = {}
        else:
            payloadDict = existing_payload
        for key, value in kwargs.iteritems():
            payloadDict[key] = value
        return payloadDict

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

        return self._Port.asdict()

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
        if self.port.has_channel('tready'):
            wait_str += " && (" + self.name + "_tready == 1)"
        thread.wait_level(wait_str, data)

    def file_to_stream(self, thread, filePath, parsingFunc=None, endian='little'):
        """
        Converts the provided file into a series of AXIS transactions.
        
        Args:
            thread (Thread): Thread to stream the file in
            filePath (str): Path to the file to stream
            parsingFunc (Func, optional): Defaults to None. Function that 
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
        if parsingFunc is None:
            parsingFunc = self._f2sBinData
        if filePath.endswith('.bin'):
            with open(filePath) as f:
                transactions = parsingFunc(f, endian)
        else:
            raise NotImplementedError()

        self._write(thread, transactions)

    def _file_to_stream(self, thread, openFile, parsingFunc, endian):
        """
        Internal variant of file_to_stream where the file has already been 
        opened, there are no optional arguments, and there is a return value
        
        Args:
            thread (Thread): Thread to stream the file in
            openFile (File): An opened file object
            parsingFunc (Function): A function object to interpret the file with
            endian (str): 'little' or 'big'
        
        Returns:
            dict: Dictionary representing the data transaction
        """

        transactions = []
        transactions = parsingFunc(openFile, endian)
        return self._write(thread, transactions)
    
    def _f2sBinData(self, data, endian):
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
        fileSize = len(data)
        beatCount = (ceil(fileSize/8.0)) * 8
        beat = 0
        tdataBytes = self.port.get_channel('tdata')['size'] / 8
        
        while beat < beatCount:           
            tdata = 0
            for i in range(beat, beat + tdataBytes):
                if endian == 'little':
                    if i < fileSize:
                        tdata = (tdata >> 8) | ( data[i] << 56) 
                    elif i < beat + tdataBytes:
                        tdata = tdata >> 8
                else: # big endian
                    if i < fileSize:
                        tdata = (tdata << 8) | ( data[i]) 
                    elif i < beat + tdataBytes:
                        tdata = tdata << 8
            payload = self._payload(tdata="0x" + format(tdata, '08x'))
           
            if self.port.has_channel('tkeep'):
                tkeep = self._f2sTkeep(fileSize, tdataBytes, beat, endian)
                payload = self._payload(payload, tkeep=tkeep)
            if self.port.has_channel('tlast'):
                tlast = self._f2sTlast(fileSize, beat)
                payload = self._payload(payload, tlast=tlast)
            
            transactions.append(payload) 
            beat = beat + tdataBytes

        return transactions

    @staticmethod
    def _f2sTkeep(fileSize, tdataBytes, beat, endian):
        """
        Calculates tkeep for a particular beat for file_to_stream since the last 
        beat may be smaller than a word.
        
        Args:
            fileSize (int): Size of data in bytes to send over tdata
            tdataBytes (int): Width of tdata in bytes
            beat (int): Beat counter
            endian (str): little|big
        
        Returns:
            str: Tkeep value for the current beat
        """

        if beat < ((ceil(fileSize/8.0) - 1) * 8.0) :
            tkeep = "KEEP_ALL"
        else:
            sizeofLastTransaction = fileSize % tdataBytes 
            if sizeofLastTransaction != tdataBytes:
                tkeep = ''
                for i in range(sizeofLastTransaction):
                    tkeep = tkeep + '1'
                if endian != 'little':
                    for i in range(tdataBytes - sizeofLastTransaction):
                        tkeep = tkeep + '0'
                tkeep = "0b" + tkeep
            else:
                tkeep = "KEEP_ALL"
        return tkeep

    @staticmethod
    def _f2sTlast(fileSize, beat):
        """
        Calculates tlast for a particular beat for file_to_stream. The last beat 
        must assert tlast
        
        Args:
            fileSize (int): Size of data in bytes to send over tdata
            beat (int): Beat counter
        
        Returns:
            str: Tlast value for the current beat
        """

        tlast = 0
        if beat >= ((ceil(fileSize/8.0) - 1) * 8) :
            tlast = 1
        return tlast        

    class _Port(InterfacePort):
        def __init__(self, name, direction, clock, c_struct, c_stream):
            """
            Initializes an InterfacePort for AXI Stream
            
            Args:
                name (str): Name of the AXIS interface
                direction (str): slave|master
                clock (str): Name of associated clock
                c_struct (str): See below
                c_stream (str): See below
                    See the docstring for AXIS.__init__(). These are used for
                    C++ simulation and represent the HLS stream struct
            """

            super(AXIS._Port, self).__init__(name, direction)
            self.type = 'axis'
            self.clock = clock
            self.c_struct = c_struct
            self.c_stream = c_stream

        def init_channels(self, mode, dataWidth=None, nameToUpperCase=True):
            """
            Initialize the channels associated with this AXIS interface. Initialize
            means to specify the names, types and widths of all the channels.
            
            Args:
                mode (str): Name of a channel preset to use. Options are:
                    'default': tdata, tvalid, tready, tlast
                    'tkeep': tdata, tvalid, tready, tlast, tkeep
                    'min': tdata, tvalid
                dataWidth (number): Width of the tdata field
                nameToUpperCase (bool, optional): Defaults to True. Assume that 
                    the channel names are the uppercase versions of their type, 
                    which is the default for an HLS module. Setting it to False 
                    sets the name identical to the type (i.e. lowercase)
            
            Raises:
                NotImplementedError: Unhandled exception if bad mode entered
                ValueError: Error in mode/argument association
            """

            if mode == 'default':
                if dataWidth is None:
                    print("dataWidth cannot be None")
                    raise ValueError
                channels = [
                    {'name': 'tdata', 'type': 'tdata', 'size': dataWidth},
                    {'name': 'tvalid', 'type': 'tvalid'},
                    {'name': 'tready', 'type': 'tready'},
                    {'name': 'tlast', 'type': 'tlast'}
                ]
            elif mode == 'tkeep':
                if dataWidth is None:
                    print("dataWidth cannot be None")
                    raise ValueError
                channels = [
                    {'name': 'tdata', 'type': 'tdata', 'size': dataWidth},
                    {'name': 'tvalid', 'type': 'tvalid'},
                    {'name': 'tready', 'type': 'tready'},
                    {'name': 'tlast', 'type': 'tlast'},
                    {'name': 'tkeep', 'type': 'tkeep', 'size': dataWidth/8}
                ]
            elif mode == 'min':
                if dataWidth is None:
                    print("dataWidth cannot be None")
                    raise ValueError
                channels = [
                    {'name': 'tdata', 'type': 'tdata', 'size': dataWidth},
                    {'name': 'tvalid', 'type': 'tvalid'}
                ]
            elif mode == 'empty':
                channels = []
            else:
                raise NotImplementedError()
            for channel in channels:
                if nameToUpperCase:
                    channel['name'] = channel['name'].upper()
            self.add_channels(channels)
        
        def asdict(self):
            """
            Returns this object as a dictionary
            
            Returns:
                dict: The fields of this object as a dictionary
            """
            port = super(AXIS._Port, self).asdict()
            port['type'] = self.type
            port['clock'] = self.clock
            if self.c_struct is not None:
                port['c_struct'] = self.c_struct
            if self.c_stream is not None:
                port['c_stream'] = self.c_stream
            return port

class SAXILite(SonarObject):
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

    def set_address(self, addrRange, addrOffset):
        """
        Sets the address range and offset for this AXI-Lite interface
        
        Args:
            addrRange (str): Address size e.g. '4K'
            addrOffset (number): Offset address
        """

        self.port.set_address(addrRange, addrOffset)

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
                address = self.port.reg_addrs[index]
                break
        transaction = {'interface': {
            'type': 's_axilite','name': self.name, 'payload': [
                {'mode': 1, 'data': data, 'addr': address}
            ]
        }}
        thread._add_transaction(transaction)

    def read(self, thread, register, expectedValue):
        """
        Read data from a register to verify its value
        
        Args:
            thread (Thread): Thread in which to read from
            register (str): Name of the register to read
            expectedValue (number): Expected value that the register should have
        """

        address = None
        for index, reg in enumerate(self.port.registers):
            if reg == register:
                address = self.port.reg_addrs[index]
                break
        transaction = {'interface': {
            'type': 's_axilite','name': self.name, 'payload': [
                {'mode': 0, 'data': expectedValue, 'addr': address}
            ]
        }}
        thread._add_transaction(transaction)

    def asdict(self):
        """
        Returns this object as a dictionary
        
        Returns:
            dict: The fields of this object as a dictionary
        """

        return self._Port.asdict() 

    class _Port(InterfacePort):

        def __init__(self, name, clock, reset):
            """
            Initialize an interface port for AXILite
            
            Args:
                name (str): Name of the interface port
                clock (str): Name of associated clock
                reset (str): Name of associated reset
            """

            super(SAXILite._Port, self).__init__(name, 'mixed')
            self.type = 's_axilite'
            self.clock = clock
            self.reset = reset
            self.connection_mode = 'ip'
            self.registers = []
            self.reg_addrs = []
            self.addr_range = ''
            self.addr_offset = ''

        def set_address(self, addrRange, addrOffset):
            """
            Sets the address range and offset for this AXI-Lite interface
            
            Args:
                addrRange (str): Address size e.g. '4K'
                addrOffset (number): Offset address
            """

            self.addr_range = addrRange
            self.addr_offset = addrOffset

        def add_register(self, name, address):
            """
            Add a register to this interface
            
            Args:
                name (str): Name of the register to add
                address (number): Address of the register
            """

            self.registers.append(name)
            self.reg_addrs.append(address)

        def del_register(self, name):
            """
            Delete a register from this interface
            
            Args:
                name (str): Name of the register to delete
            """

            for index, name_ in enumerate(self.registers):
                if name_ == name:
                    del self.registers[index]
                    del self.reg_addrs[index]
                    break

        def init_channels(self, mode, dataWidth=None, addrWidth=None, nameToUpperCase=True):
            """
            Initialize the channels associated with this AXILite interface. 
            Initialize means to specify the names, types and widths of all the 
            channels.
            
            Args:
                mode (str): Name of a channel preset to use. Options are:
                    'default': standard AXI-Lite without cache or prot
                dataWidth (number): Width of the data channel (r/w)
                addrWidth (number): Width of the addr channel (r/w)
                nameToUpperCase (bool, optional): Defaults to True. Assume that 
                    the channel names are the uppercase versions of their type, 
                    which is the default for an HLS module. Setting it to False 
                    sets the name identical to the type (i.e. lowercase)
            
            Raises:
                NotImplementedError: Unhandled exception if bad mode entered
                ValueError: Error in mode/argument association
            """
            if mode == 'default':
                if dataWidth is None or addrWidth is None:
                    print("dataWidth or addrWidth cannot be None")
                    raise ValueError
                channels = [
                    {'name': 'awvalid', 'type': 'awvalid'},
                    {'name': 'awready', 'type': 'awready'},
                    {'name': 'awaddr', 'type': 'awaddr', 'size': addrWidth},
                    {'name': 'wvalid', 'type': 'wvalid'},
                    {'name': 'wready', 'type': 'wready'},
                    {'name': 'wdata', 'type': 'wdata', 'size': dataWidth},
                    {'name': 'wstrb', 'type': 'wstrb', 'size': dataWidth/8},
                    {'name': 'arvalid', 'type': 'arvalid'},
                    {'name': 'arready', 'type': 'arready'},
                    {'name': 'araddr', 'type': 'araddr', 'size': addrWidth},
                    {'name': 'rvalid', 'type': 'rvalid'},
                    {'name': 'rready', 'type': 'rready'},
                    {'name': 'rdata', 'type': 'rdata', 'size': dataWidth},
                    {'name': 'rresp', 'type': 'rresp', 'size': 2},
                    {'name': 'bvalid', 'type': 'bvalid'},
                    {'name': 'bready', 'type': 'bready'},
                    {'name': 'bresp', 'type': 'bresp', 'size': 2}
                ]
            elif mode == 'empty':
                channels = []
            else:
                raise NotImplementedError
            for channel in channels:
                if nameToUpperCase:
                    channel['name'] = channel['name'].upper()
            self.add_channels(channels)

        def asdict(self):
            """
            Returns this object as a dictionary
            
            Returns:
                dict: The fields of this object as a dictionary
            """
            port = port = super(SAXILite._Port, self).asdict()
            port['type'] = self.type
            port['clock'] = self.clock
            port['reset'] = self.reset
            port['registers'] = self.registers
            port['reg_addrs'] = self.reg_addrs
            port['addr_offset'] = self.addr_offset
            port['addr_range'] = self.addr_range
            port['connection_mode'] = self.connection_mode
            return port
