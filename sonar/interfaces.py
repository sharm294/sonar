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
        Writes the given command to the AXIS stream.

        Args:
            data (str): Data to write
            kwargs (str): keyworded arguments where the keyword is the AXIS 
                channel or special keyword and is assigned to the given value
        Returns:
            dict: Dictionary representing the data transaction
        """
        payloadDict = self.payload(data, **kwargs)
        payloadArg = [payloadDict]
        transaction = {'interface': {
            'type': 'axis','name': self.name, 'payload': payloadArg
        }}
        thread.add_transaction(transaction)
    
    def writes(self, thread, payload):
        """
        Writes the given payload to the AXIS stream.

        Args:
            payload (list): Directly assigns a list containing valid 
                transaction dicts to be written

        Returns:
            dict: Dictionary representing the data transaction
        """

        payloadArg = payload
        transaction = {'interface': {
            'type': 'axis','name': self.name, 'payload': payloadArg
        }}
        thread.add_transaction(transaction)

    def payload(self, data, **kwargs):
        payloadDict = {}
        payloadDict['tdata'] = data
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
        # thread.add_transaction(transaction)

    def asdict(self):
        """
        Returns this object as a dictionary
        
        Returns:
            dict: The fields of this object as a dictionary
        """

        return self._Port.asdict()        

    def file_to_stream(self, thread, filePath, parsingFunc=None, endian='little'):
        """
        Converts the provided file into a series of AXIS transactions.
        
        Args:
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

        self.writes(thread, transactions)

    def _file_to_stream(self, thread, openFile, parsingFunc, endian):
        transactions = []
        transactions = parsingFunc(openFile, endian)
        return self.writes(thread, transactions)
    
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
            payload = {}
            
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
            payload['tdata'] = "0x" + format(tdata, '08x')
           
            if self.port.has_channel('tkeep'):
                payload['tkeep'] = self._f2sTkeep(
                    fileSize, tdataBytes, beat, endian
                )
            if self.port.has_channel('tlast'):
                payload['tlast'] = self._f2sTlast(
                    fileSize, beat
                )
            
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
                # for i in range(0, tdataBytes - sizeofLastTransaction):
                #     if endian == 'little':
                #         tkeep = tkeep + "0" 
                #     else: # big endian
                #         tkeep = "0" + tkeep 
                # for i in range(tdataBytes - sizeofLastTransaction, tdataBytes):
                #     if endian == 'little':
                #         tkeep = tkeep + "1"
                #     else: # big endian
                #         tkeep = "1" + tkeep
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
            super(AXIS._Port, self).__init__(name, direction)
            self.type = 'axis'
            self.clock = clock
            self.c_struct = c_struct
            self.c_stream = c_stream

        def init_channels(self, mode, dataWidth, nameToUpperCase=True):
            if mode == 'default':
                channels = [
                    {'name': 'tdata', 'type': 'tdata', 'size': dataWidth},
                    {'name': 'tvalid', 'type': 'tvalid'},
                    {'name': 'tready', 'type': 'tready'},
                    {'name': 'tlast', 'type': 'tlast'}
                ]
            elif mode == 'tkeep':
                channels = [
                    {'name': 'tdata', 'type': 'tdata', 'size': dataWidth},
                    {'name': 'tvalid', 'type': 'tvalid'},
                    {'name': 'tready', 'type': 'tready'},
                    {'name': 'tlast', 'type': 'tlast'},
                    {'name': 'tkeep', 'type': 'tkeep', 'size': dataWidth/8}
                ]
            else:
                raise NotImplementedError()
            for channel in channels:
                if nameToUpperCase:
                    channel['name'] = channel['name'].upper()
            self.add_channels(channels)
        
        def asdict(self):
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
        self.name = name
        self.port = self._Port(name, clock, reset)

    def set_address(self, addrRange, addrOffset):
        self.port.set_address(addrRange, addrOffset)

    def add_register(self, name, address):
        self.port.add_register(name, address)

    def delRegister(self, name):
        self.port.delRegister(name)

    def write(self, thread, register, data):
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
        thread.add_transaction(transaction)

    def read(self, thread, register, expectedValue):
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
        thread.add_transaction(transaction)

    def asdict(self):
        return self._Port.asdict() 

    class _Port(InterfacePort):

        def __init__(self, name, clock, reset):
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
            self.addr_range = addrRange
            self.addr_offset = addrOffset

        def add_register(self, name, address):
            self.registers.append(name)
            self.reg_addrs.append(address)

        def delRegister(self, name):
            for index, name_ in enumerate(self.registers):
                if name_ == name:
                    del self.registers[index]
                    del self.reg_addrs[index]
                    break

        def init_channels(self, mode, dataWidth, addrWidth, nameToUpperCase=True):
            if mode == 'default':
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
            else:
                raise NotImplementedError
            for channel in channels:
                if nameToUpperCase:
                    channel['name'] = channel['name'].upper()
            self.add_channels(channels)

        def asdict(self):
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
