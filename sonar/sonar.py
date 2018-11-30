class SonarDict(dict):

    @classmethod
    def initFromDict(cls, dictArg):
        port = cls()
        for key, value in dictArg.iteritems():
            port[key] = value
        return port


class Sonar(SonarDict):

    @classmethod
    def init(cls):
        sonar = cls()
        sonar['metadata'] = {
            'Module_Name': None,
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
        sonar['waitConditions'] = []
        sonar['modules'] = []
        sonar['vectors'] = []
        return sonar

    def addMetadata(self, key, value):
        self['metadata'][key] = value

    def addModule(self, module):
        self['modules'].append(module)

    def addTestVector(self, vector):
        self['vectors'].append(vector)

    def finalizeWaits(self):
        waits = []
        conditions = set()
        flagPresent = False
        index = 0
        for vector in self['vectors']:
            for thread in vector:
                for command in thread:
                    if 'wait' in command:
                        tempKey = command['wait']['key']
                        # print(tempKey)
                        if tempKey == 'flag':
                            flagPresent = True
                            continue
                        if tempKey not in conditions:
                            newKey = 'w' + str(index)
                            waits.append({'condition': tempKey, 'key': newKey})
                            conditions.add(tempKey)
                            index += 1
                        else:
                            for wait in waits:
                                if wait['condition'] == tempKey:
                                    key = wait['key']
                                    break
                            command['wait']['key'] = key
        if flagPresent:
            waits.append({"condition": "wait(flags[$value]);", "key": "flag"})
        self['waitConditions'] = waits


class Module(SonarDict):

    @classmethod
    def init(cls, name):
        """
        Create an empty module

        :param name: The name of the module to create
        :returns: A Module object
        """
        module = cls()
        module['name'] = name
        module['ports'] = []
        return module

    def addPort(self, name, size=1, **kwargs):
        port = {}
        port['name'] = name
        port['size'] = size
        for key, value in kwargs.iteritems():
            port[key] = value
        self['ports'].append(port)

    def addClockPort(self, name, period):
        port = {}
        port['name'] = name
        port['size'] = 1
        port['type'] = 'clock'
        port['period'] = period
        self['ports'].append(port)

    def addResetPort(self, name):
        port = {}
        port['name'] = name
        port['size'] = 1
        port['type'] = 'reset'
        self['ports'].append(port)

    def addInterface(self, interface):
        self['ports'].append(interface)

class InterfacePort(SonarDict):

    def __init__(self, direction):
        self['direction'] = direction
        self['channels'] = []

    def addKey(self, key, value):
        self[key] = value

    def delKey(self, key):
        del self[key]

    def addChannel(self, name, channelType, size=1):
        channel = {}
        channel['name'] = name
        channel['type'] = channelType
        channel['size'] = size
        self['channels'].append(channel)

    def addChannels(self, channels):
        for channel in channels:
            channelDict = {}
            channelDict['name'] = channel[0]
            channelDict['type'] = channel[1]
            if len(channel) == 3:
                channelDict['size'] = channel[2]
            else:
                channelDict['size'] = 1
            self['channels'].append(channelDict)

class AXIS(object):
    def __init__(self, name, direction, clock, c_struct=None, c_stream=None):
        self.name = name
        self.port = self._Port.init(direction, clock, c_struct, c_stream)

    def write(self, **kwargs):
        payload = {}
        for key, value in kwargs.iteritems():
            payload[key] = value
        transaction = {'interface': {
            'type': 'axis','name': self.name, 'payload': [
                payload
            ]
        }}
        return transaction

    def read(self, **kwargs):
        self.write(kwargs)

    class _Port(InterfacePort):

        @classmethod
        def init(cls, direction, clock, c_struct, c_stream):
            interface = cls(direction)
            interface['type'] = 'axis'
            interface['clock'] = clock
            interface['c_struct'] = c_struct
            interface['c_stream'] = c_stream
            return interface

        def initChannels(self, mode, dataWidth):
            if mode == 'DEFAULT':
                channels = [
                    ['TDATA', 'tdata', dataWidth],
                    ['TVALID', 'tvalid'],
                    ['TREADY', 'tready'],
                    ['TLAST', 'tlast']
                ]
            elif mode == 'default':
                channels = [
                    ['tdata', 'tdata', dataWidth],
                    ['tvalid', 'tvalid'],
                    ['tready', 'tready'],
                    ['tlast', 'tlast']
                ]
            else:
                raise NotImplementedError
            self.addChannels(channels)

class SAXILite(object):
    def __init__(self, name, clock, reset):
        self.name = name
        self.port = self._Port.init(clock, reset)

    def setAddress(self, addrRange, addrOffset):
        self.port.setAddress(addrRange, addrOffset)

    def addRegister(self, name, address):
        self.port.addRegister(name, address)

    def delRegister(self, name):
        self.port.delRegister(name)

    def write(self, register, data):
        address = None
        for index, reg in enumerate(self.port['registers']):
            if reg == register:
                address = self.port['regAddrs'][index]
                break
        transaction = {'interface': {
            'type': 's_axilite','name': self.name, 'payload': [
                {'mode': 1, 'data': data, 'addr': address}
            ]
        }}
        return transaction

    def read(self, register, expectedValue):
        address = None
        for index, reg in enumerate(self.port['registers']):
            if reg == register:
                address = self.port['regAddrs'][index]
                break
        transaction = {'interface': {
            'type': 's_axilite','name': self.name, 'payload': [
                {'mode': 0, 'data': expectedValue, 'addr': address}
            ]
        }}
        return transaction

    class _Port(InterfacePort):

        @classmethod
        def init(cls, clock, reset):
            interface = cls('mixed')
            interface['type'] = 's_axilite'
            interface['clock'] = clock
            interface['reset'] = reset
            interface['connectionMode'] = 'ip'
            interface['registers'] = []
            interface['regAddrs'] = []
            return interface

        def setAddress(self, addrRange, addrOffset):
            self['addr_range'] = addrRange
            self['addr_offset'] = addrOffset

        def addRegister(self, name, address):
            self['registers'].append(name)
            self['regAddrs'].append(address)

        def delRegister(self, name):
            for index, name_ in enumerate(self['registers']):
                if name_ == name:
                    del self['registers'][index]
                    del self['regAddrs'][index]
                    break

        def initChannels(self, mode, dataWidth, addrWidth):
            if mode == 'DEFAULT':
                channels = [
                    ['AWVALID', 'awvalid'],
                    ['AWREADY', 'awready'],
                    ['AWADDR', 'awaddr', addrWidth],
                    ['WVALID', 'wvalid'],
                    ['WREADY', 'wready'],
                    ['WDATA', 'wdata', dataWidth],
                    ['WSTRB', 'wstrb', dataWidth/8],
                    ['ARVALID', 'arvalid'],
                    ['ARREADY', 'arready'],
                    ['ARADDR', 'araddr', addrWidth],
                    ['RVALID', 'rvalid'],
                    ['RREADY', 'rready'],
                    ['RDATA', 'rdata', dataWidth],
                    ['RRESP', 'rresp', 2],
                    ['BVALID', 'bvalid'],
                    ['BREADY', 'bready'],
                    ['BRESP', 'bresp', 2]
                ]
            elif mode == 'default':
                channels = [
                    ['awvalid', 'awvalid'],
                    ['awready', 'awready'],
                    ['awaddr', 'awaddr', addrWidth],
                    ['wvalid', 'wvalid'],
                    ['wready', 'wready'],
                    ['wdata', 'wdata', dataWidth],
                    ['wstrb', 'wstrb', dataWidth/8],
                    ['arvalid', 'arvalid'],
                    ['arready', 'arready'],
                    ['araddr', 'araddr', addrWidth],
                    ['rvalid', 'rvalid'],
                    ['rready', 'rready'],
                    ['rdata', 'rdata', dataWidth],
                    ['rresp', 'rresp', 2],
                    ['bvalid', 'bvalid'],
                    ['bready', 'bready'],
                    ['bresp', 'bresp', 2]
                ]
            else:
                raise NotImplementedError
            self.addChannels(channels)

class TestVector(list):

    def addThread(self, thread):
        self.append(thread)

class Thread(list):

    def addDelay(self, delay):
        self.append({'delay': delay})

    def setSignal(self, name, value):
        self.append({'signal': {'name': name, 'value': value}})

    def initSignals(self):
        self.append({'macro': 'INIT_SIGNALS'})

    def initTimer(self):
        self.append({'timestamp': 'INIT'})

    def printElapsedTime(self, id):
        self.append({'timestamp': id})
    
    def display(self, string):
        self.append({'display': string})

    def endVector(self):
        self.append({'macro': 'END'})

    def setFlag(self, id):
        self.append({'flag': {'set_flag': id}})

    def waitFlag(self, id):
        self.append({'wait': {'key': 'flag', 'value': id}})
        self.append({'flag': {'clear_flag': id}})

    def wait(self, condition, value=None):
        if value is None:
            self.append({'wait': {'key': condition}})
        else:
            self.append({'wait': {'key': condition, 'value': value}})

    def waitLevel(self, condition, value=None):
        conditionTmp = 'wait(' + condition + ');'
        if value is None:
            self.append({'wait': {'key': conditionTmp}})
        else:
            self.append({'wait': {'key': conditionTmp}, 'value': value})

    def waitEdge(self, risingEdge, signal):
        if risingEdge:
            edge = 'posedge '
        else:
            edge = 'negedge '
        conditionTmp = '@(' + edge + signal + ');'
        self.append({'wait': {'key': conditionTmp}})

    def addInterfaceTransaction(self, transaction):
        self.append(transaction)


if __name__ == "__main__":

    print("Sonar Test Module")
    print("*****************\n")

    sonar = Sonar.init()
    sonar.addMetadata('Module_Name', 'sample')

    dut = Module.init("dut")
    dut.addClockPort("ap_clk", "20ns")
    dut.addResetPort("ap_rst_n")
    dut.addPort("state_out_V", size=3, direction="output")
    dut.addPort("ack_V", direction="output")
    sonar.addModule(dut)

    axis_out = AXIS("axis_output", "master", "ap_clk")
    axis_out.port.initChannels('DEFAULT', 64)
    # axis_out.port.addChannel('TKEEP', 'tkeep', 8) # e.g. to add a new channel
    dut.addInterface(axis_out.port)

    axis_in = AXIS("axis_input", "slave", "ap_clk")
    axis_in.port.initChannels('DEFAULT', 64)
    dut.addInterface(axis_in.port)

    ctrl_bus = SAXILite('s_axi_ctrl_bus', 'ap_clk', 'ap_rst_n')
    ctrl_bus.addRegister('enable', 0x10)
    ctrl_bus.setAddress('4K', 0)
    ctrl_bus.port.initChannels(mode='DEFAULT', dataWidth=32, addrWidth=5)
    dut.addInterface(ctrl_bus.port)

    testVector0 = TestVector()
    
    initT = Thread()
    initT.waitEdge(False, 'ap_clk')
    initT.initSignals()
    initT.addDelay('40ns')
    initT.setSignal('ap_rst_n', 1)
    initT.setSignal('axis_output_tready', 1)
    testVector0.addThread(initT)

    inputT = Thread()
    inputT.addDelay('100ns')
    inputT.initTimer()
    inputT.addInterfaceTransaction(ctrl_bus.write('enable', 1))
    inputT.addInterfaceTransaction(axis_in.write(tdata=0xABCD, callTB=2))
    inputT.waitLevel('ack_V == $value', 1)
    inputT.addInterfaceTransaction(axis_in.write(tdata=0,callTB=3))
    inputT.waitLevel('ack_V == $value', 1)
    inputT.addDelay('110ns')
    inputT.setFlag(0)
    testVector0.addThread(inputT)

    outputT = Thread()
    outputT.addInterfaceTransaction(axis_out.read(tdata=1))
    outputT.waitFlag(0)
    outputT.addInterfaceTransaction(ctrl_bus.read('enable', 1))
    outputT.printElapsedTime('End')
    outputT.display('The_simulation_is_finished')
    outputT.endVector()
    testVector0.addThread(outputT)

    sonar.addTestVector(testVector0)
    sonar.finalizeWaits()

    import pprint
    pprint.pprint(sonar)