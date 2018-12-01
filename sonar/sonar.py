import json

class SonarObject(object):
    def __str__(self):
        return json.dumps(self.asdict())

    def asdict(self):
        raise NotImplementedError # overridden in the child class

class Sonar(SonarObject):

    def __init__(self):
        self.metadata = {}
        self.wait_conditions = []
        self.modules = []
        self.vectors = []

    @classmethod
    def default(cls, module_name):
        """
        Initializes a sonar testbench with default metadata values

        :param module_name: The name of the module to create

        :returns: A Sonar object
        """
        sonar = cls()
        sonar.metadata = {
            'Module_Name': module_name,
            'Timescale': '1ns / 1ps',
            'Time_Format': {'unit': '1us', 'precision': 3},
            'Flag_Count': 1,
            'Company': None,
            'Engineer': None,
            'Project_Name': None,
            'Target_Devices': None,
            'Tool_Versions': None,
            'Description': None,
            'Dependencies': None
        }
        return sonar

    def add_metadata(self, key, value):
        if key in self.metadata:
            raise KeyError('Key ' + key + ' already exists in metadata')
        self.metadata[key] = value

    def set_metadata(self, key, value):
        if key not in self.metadata:
            raise KeyError('Key ' + key + ' does not exist in metadata')
        self.metadata[key] = value

    def add_module(self, module):
        self.modules.append(module)

    def add_test_vector(self, vector):
        self.vectors.append(vector)

    def finalize_waits(self):
        waits = []
        conditions = []
        flagPresent = False
        index = 0
        for vector in self.vectors:
            for thread in vector.threads:
                for command in thread.commands:
                    if 'wait' in command:
                        tempKey = command['wait']['key']
                        if tempKey == 'flag':
                            flagPresent = True
                            continue
                        if tempKey not in conditions:
                            newKey = 'w' + str(index)
                            waits.append({'condition': tempKey, 'key': newKey})
                            conditions.append(tempKey)
                            index += 1
                            command['wait']['key'] = newKey
                        else:
                            for wait in waits:
                                if wait['condition'] == tempKey:
                                    key = wait['key']
                                    break
                            command['wait']['key'] = key
        if flagPresent:
            waits.append({"condition": "wait(flags[$value]);", "key": "flag"})
        self.wait_conditions = waits

    def asdict(self):
        sonar_dict = {}
        sonar_dict['metadata'] = self.metadata
        modules = []
        for module in self.modules:
            modules.append(module.asdict())
        sonar_dict['modules'] = modules
        sonar_dict['wait_conditions'] = self.wait_conditions
        vectors = []
        for vector in self.vectors:
            vectors.append(vector.asdict())
        sonar_dict['vectors'] = vectors
        return sonar_dict

class Module(SonarObject):

    def __init__(self):
        self.name = ""
        self.ports = []

    @classmethod
    def default(cls, name):
        """
        Creates an empty Module

        :param name: The name of the module to create

        :returns: A Module object
        """
        module = cls()
        module.name = name
        return module

    def add_port(self, name, direction, size=1):
        port = {}
        port['name'] = name
        port['size'] = size
        port['direction'] = direction
        self.ports.append(port)

    def add_clock_port(self, name, period):
        port = {}
        port['name'] = name
        port['size'] = 1
        port['type'] = 'clock'
        port['period'] = period
        port['direction'] = 'input'
        self.ports.append(port)

    def add_reset_port(self, name):
        port = {}
        port['name'] = name
        port['size'] = 1
        port['type'] = 'reset'
        port['direction'] = 'input'
        self.ports.append(port)

    def add_interface(self, interface):
        self.ports.append(interface)

    def asdict(self):
        module = {}
        module['name'] = self.name
        module['ports'] = []
        for port in self.ports:
            if isinstance(port, InterfacePort):
                module['ports'].append(port.asdict())
            else:
                module['ports'].append(port)
        return module

class InterfacePort(SonarObject):

    def __init__(self, name, direction):
        self.name = name
        self.direction = direction
        self.channels = []

    def add_channel(self, name, channelType, size=1):
        channel = {}
        channel['name'] = name
        channel['type'] = channelType
        channel['size'] = size
        self.channels.append(channel)

    def add_channels(self, channels):
        for channel in channels:
            if isinstance(channel, list):
                name = channel[0]
                channelType = channel[1]
                if len(channel) == 3:
                    size = channel[2]
                else:
                    size = 1
            elif isinstance(channel, dict):
                name = channel['name']
                channelType = channel['type']
                if 'size' in channel:
                    size = channel['size']
                else:
                    size = 1
            else:
                raise NotImplementedError()
            self.add_channel(name, channelType, size)

    def get_channel(self, channelType):
        channel_dict = None
        for channel in self.channels:
            if channel['type'] == channelType:
                channel_dict = channel
                break
        if channel_dict is None:
            raise KeyError()
        return channel_dict

    def has_channel(self, channelType):
        channel_exists = False
        for channel in self.channels:
            if channel['type'] == channelType:
                channel_exists = True
                break
        return channel_exists

    def asdict(self):
        port = {}
        port['name'] = self.name
        port['direction'] = self.direction
        port['channels'] = self.channels
        return port

class AXIS(SonarObject):

    def __init__(self, name, direction, clock, c_struct=None, c_stream=None):
        self.name = name
        self.port = self._Port(name, direction, clock, c_struct, c_stream)

    def write(self, **kwargs):
        payload = {}
        for key, value in kwargs.iteritems():
            payload[key] = value
        transaction = {'interface': {
            'type': 'axis','name': self.name, 'payload': [payload]
        }}
        return transaction

    def read(self, **kwargs):
        transaction = self.write(**kwargs)
        return transaction

    def asdict(self):
        return self._Port.asdict()        

    # def fileToStream(self, dataFile, parsingFunction=None,)
        

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
            port['c_struct'] = self.c_struct
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

class TestVector(SonarObject):
    
    def __init__(self, thread=None, threads=None):
        self.threads = []
        if thread is not None:
            self.threads.append(thread)
        if threads is not None:
            for t in threads:
                self.threads.append(t)

    def addThread(self, thread=None):
        if thread is None:
            thread = Thread()
        self.threads.append(thread)

    def asdict(self):
        threads = []
        for thread in self.threads:
            threads.append(thread.asdict())
        return threads

class Thread(SonarObject):

    def __init__(self):
        self.commands = []

    def add_delay(self, delay):
        self.commands.append({'delay': delay})

    def set_signal(self, name, value):
        self.commands.append({'signal': {'name': name, 'value': value}})

    def init_signals(self):
        self.commands.append({'macro': 'INIT_SIGNALS'})

    def initTimer(self):
        self.commands.append({'timestamp': 'INIT'})

    def print_elapsed_time(self, id):
        self.commands.append({'timestamp': id})
    
    def display(self, string):
        self.commands.append({'display': string})

    def end_vector(self):
        self.commands.append({'macro': 'END'})

    def set_flag(self, id):
        self.commands.append({'flag': {'set_flag': id}})

    def wait_flag(self, id):
        self.commands.append({'wait': {'key': 'flag', 'value': id}})
        self.commands.append({'flag': {'clear_flag': id}})

    def wait(self, condition, value=None):
        if value is None:
            self.commands.append({'wait': {'key': condition}})
        else:
            self.commands.append({'wait': {'key': condition, 'value': value}})

    def wait_level(self, condition, value=None):
        conditionTmp = 'wait(' + condition + ');'
        if value is None:
            self.commands.append({'wait': {'key': conditionTmp}})
        else:
            self.commands.append({'wait': {'key': conditionTmp}, 'value': value})

    def wait_edge(self, risingEdge, signal):
        if risingEdge:
            edge = 'posedge '
        else:
            edge = 'negedge '
        conditionTmp = '@(' + edge + signal + ');'
        self.commands.append({'wait': {'key': conditionTmp}})

    def add_transaction(self, transaction):
        self.commands.append(transaction)

    def add_interfaceTransactions(self, transactions):
        for transaction in transactions:
            self.commands.append(transaction)

    def asdict(self):
        commands = []
        for command in self.commands:
            commands.append(command)
        return commands

if __name__ == "__main__":

    print("Sonar Test Module")
    print("*****************\n")

    sonar = Sonar.default('sample')
    sonar.set_metadata('Module_Name', 'sample')

    dut = Module.default("dut")
    dut.add_clock_port("ap_clk", "20ns")
    dut.add_reset_port("ap_rst_n")
    dut.add_port("state_out_V", size=3, direction="output")
    dut.add_port("ack_V", direction="output")
    sonar.add_module(dut)

    axis_out = AXIS("axis_output", "master", "ap_clk")
    axis_out.port.init_channels('default', 64)
    # axis_out.ports.addChannel('TKEEP', 'tkeep', 8) # e.g. to add a new channel
    dut.add_interface(axis_out.port)

    axis_in = AXIS("axis_input", "slave", "ap_clk")
    axis_in.port.init_channels('default', 64)
    dut.add_interface(axis_in.port)

    ctrl_bus = SAXILite('s_axi_ctrl_bus', 'ap_clk', 'ap_rst_n')
    ctrl_bus.add_register('enable', 0x10)
    ctrl_bus.set_address('4K', 0)
    ctrl_bus.port.init_channels(mode='default', dataWidth=32, addrWidth=5)
    dut.add_interface(ctrl_bus.port)

    test_vector_0 = TestVector()
    
    initT = Thread()
    initT.wait_edge(False, 'ap_clk')
    initT.init_signals()
    initT.add_delay('40ns')
    initT.set_signal('ap_rst_n', 1)
    initT.set_signal('axis_output_tready', 1)
    test_vector_0.addThread(initT)

    inputT = Thread()
    inputT.add_delay('100ns')
    inputT.initTimer()
    inputT.add_transaction(ctrl_bus.write('enable', 1))
    inputT.add_transaction(axis_in.write(tdata=0xABCD, callTB=2))
    inputT.wait_level('ack_V == $value', value=1)
    inputT.add_transaction(axis_in.write(tdata=0,callTB=3))
    inputT.wait_level('ack_V == $value', value=1)
    inputT.add_delay('110ns')
    inputT.set_flag(0)
    test_vector_0.addThread(inputT)

    outputT = Thread()
    outputT.add_transaction(axis_out.read(tdata=1))
    outputT.wait_flag(0)
    outputT.add_transaction(ctrl_bus.read('enable', 1))
    outputT.print_elapsed_time('End')
    outputT.display('The_simulation_is_finished')
    outputT.end_vector()
    test_vector_0.addThread(outputT)

    sonar.add_test_vector(test_vector_0)
    sonar.finalize_waits()

    import pprint
    print(sonar)
    pprint.pprint(sonar.asdict())