from .base_types import SonarObject
from .base_types import InterfacePort

class AXIS(SonarObject):

    def __init__(self, name, direction, clock, c_struct=None, c_stream=None):
        self.name = name
        self.port = self._Port(name, direction, clock, c_struct, c_stream)

    def write(self, payload=None, **kwargs):
        if payload is None: 
            payloadDict = {}
            for key, value in kwargs.iteritems():
                payloadDict[key] = value
            payloadArg = [payloadDict]
        else:
            payloadArg = payload
        transaction = {'interface': {
            'type': 'axis','name': self.name, 'payload': payloadArg
        }}
        return transaction

    def read(self, **kwargs):
        transaction = self.write(**kwargs)
        return transaction

    def asdict(self):
        return self._Port.asdict()        

    def fileToStream(self, filePath, parsingFunc=None, endian='little'):
        transactions = []
        if parsingFunc is None:
            parsingFunc = self._f2sBinData
        if filePath.endswith('.bin'):
            with open(filePath) as f:
                transactions = parsingFunc(f, endian)
        else:
            raise NotImplementedError()

        return self.write(payload=transactions)
    
    def _f2sBinData(self, dataFile, endian):
        transactions = []
        fileSize = len(dataFile)
        beatCount = (math.ceil(fileSize/8.0)) * 8
        beat = 0
        tdataBytes = self.port.get_channel('tdata')['size'] / 8
        
        while beat < beatCount:
            payload = {}
            
            tdata = 0
            for i in range(beat, beat + tdataBytes):
                if endian == 'little':
                    if i < fileSize:
                        tdata = (tdata >> 8) | ( dataFile[i] << 56) 
                    elif i < beat + tdataBytes:
                        tdata = tdata >> 8
                else: # big endian
                    if i < fileSize:
                        tdata = (tdata << 8) | ( dataFile[i]) 
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
        if beat < ((math.ceil(fileSize/8.0) - 1) * 8.0) :
            tkeep = "KEEP_ALL"
        else:
            sizeofLastTransaction = fileSize % tdataBytes 
            if sizeofLastTransaction != tdataBytes:
                tkeep = ''
                for i in range(0, tdataBytes - sizeofLastTransaction):
                    if endian == 'little':
                        tkeep = tkeep + "0" 
                    else: # big endian
                        tkeep = "0" + tkeep 
                for i in range(tdataBytes - sizeofLastTransaction, tdataBytes):
                    if endian == 'little':
                        tkeep = tkeep + "1"
                    else: # big endian
                        tkeep = "1" + tkeep
                tkeep = "0b" + tkeep
            else:
                tkeep = "KEEP_ALL"
        return tkeep

    @staticmethod
    def _f2sTlast(fileSize, beat):
        tlast = 0
        if beat >= ((math.ceil(fileSize/8.0) - 1) * 8) :
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

    def write(self, register, data):
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
        return transaction

    def read(self, register, expectedValue):
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
        return transaction

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
