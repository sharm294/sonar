import json
import math
import sys

from .base_types import SonarObject
from .base_types import InterfacePort
from .core import sonar as sonarCore

class Sonar(SonarObject):

    def __init__(self):
        """
        Initializes a Sonar object with empty attributes
        """
        
        self.metadata = {}
        self.wait_conditions = []
        self.modules = []
        self.vectors = []

    @classmethod
    def default(cls, module_name):
        """
        Initializes a sonar testbench with default metadata values

        Args:
            module_name (str): Name of the DUT module
        
        Returns:
            Sonar: the Sonar object represents the whole testbench
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
        """
        Adds metadata to the Sonar object
        
        Args:
            key (str): Key to store the value against
            value (str): Metadata to store
        
        Raises:
            KeyError: Raised if the requested key already exists
        """

        if key in self.metadata:
            raise KeyError('Key ' + key + ' already exists in metadata')
        self.metadata[key] = value

    def set_metadata(self, key, value):
        """
        Sets the metadata value of the specified key to the provided value
        
        Args:
            key (str): Key to update
            value (str): Metadata value to store
        
        Raises:
            KeyError: raised if the requested key doesn't exist
        """

        if key not in self.metadata:
            raise KeyError('Key ' + key + ' does not exist in metadata')
        self.metadata[key] = value

    def add_module(self, module):
        """
        Adds a module to the testbench
        
        Args:
            module (Module): Module to add to this testbench
        """

        self.modules.append(module)

    def add_test_vector(self, vector):
        """
        Adds a test vector to the testbench
        
        Args:
            vector (TestVector): Vector containing one or more non-empty threads
        """

        self.vectors.append(vector)

    def finalize_waits(self):
        """
        Using the test vectors in the testbench, this method aggregates all the 
        wait conditions as required for the Sonar backend. This method must be 
        called ONCE after all test vectors have been completed and added.
        """

        waits = []
        conditions = []
        flagPresent = False
        index = 0
        for vector in self.vectors:
            for thread in vector.threads:
                for command in thread.commands:
                    if 'wait' in command:
                        # print(command)
                        tempKey = command['wait']['key']
                        # print(tempKey)
                        if tempKey == 'flag':
                            flagPresent = True
                            continue
                        if tempKey.isdigit():
                            if int(tempKey) >= index:
                                raise Exception
                            continue
                        if tempKey not in conditions:
                            newKey = str(index)
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
        """
        Converts the object to a dictionary
        
        Returns:
            dict: Dictionary representing the object
        """

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

    def asjson(self):
        return json.dumps(self.asdict(), indent=2)

    def generateTB(self, directory_path, languages):
        filename = self.metadata['Module_Name']
        filepath = directory_path + filename + '.json'
        with open(filepath, 'w+') as f:
            json.dump(self.asdict(), f, indent=2)
        sonarCore.sonar('absolute', None, filepath, languages)

class Module(SonarObject):

    def __init__(self):
        """
        Initializes a module with empty attributes
        """

        self.name = ""
        self.ports = []

    @classmethod
    def default(cls, name):
        """
        Creates a default module with the given name
        
        Args:
            name (str): Name of the module to create
        
        Returns:
            Module: Object representing a module
        """

        module = cls()
        module.name = name
        return module

    def add_port(self, name, direction, size=1):
        """
        Adds a generic port for a signal to this module
        
        Args:
            name (str): Name of the signal
            direction (str): Must be one of (input|output)
            size (int, optional): Defaults to 1. Width of the port in bits
        """

        port = {}
        port['name'] = name
        port['size'] = size
        port['direction'] = direction
        self.ports.append(port)

    def add_clock_port(self, name, period):
        """
        Adds an input clock port to this module (only for TB generated clocks)
        
        Args:
            name (str): Name of the clock signal
            period (str): Period of the clock (e.g. 20ns, 10ps etc.)
        """

        port = {}
        port['name'] = name
        port['size'] = 1
        port['type'] = 'clock'
        port['period'] = period
        port['direction'] = 'input'
        self.ports.append(port)

    def add_reset_port(self, name):
        """
        Adds an input reset port to this module
        
        Args:
            name (str): Name of the reset signal
        """

        port = {}
        port['name'] = name
        port['size'] = 1
        port['type'] = 'reset'
        port['direction'] = 'input'
        self.ports.append(port)

    def add_interface(self, interface):
        """
        Adds an interface port to this module
        
        Args:
            interface (InterfacePort->child): Represents the interface port and 
                must be a child class of InterfacePort. An interface class will 
                define its port at Interface.port
        """

        self.ports.append(interface.port)

    def asdict(self):
        """
        Converts the object to a dictionary
        
        Returns:
            dict: Dictionary representing the object
        """
        module = {}
        module['name'] = self.name
        module['ports'] = []
        for port in self.ports:
            if isinstance(port, InterfacePort):
                module['ports'].append(port.asdict())
            else:
                module['ports'].append(port)
        return module



class TestVector(SonarObject):
    
    def __init__(self, thread=None, threads=None):
        self.threads = []
        if thread is not None:
            self.threads.append(thread)
        if threads is not None:
            for t in threads:
                self.threads.append(t)

    def add_thread(self, thread=None):
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
        self.commands.append({'signal': [{'name': name, 'value': value}]})

    def init_signals(self):
        self.commands.append({'macro': 'INIT_SIGNALS'})

    def init_timer(self):
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
            self.commands.append({'wait': {'key': conditionTmp, 'value': value}})

    def wait_edge(self, edge, signal):
        if edge != 'posedge' and edge != 'negedge':
            raise ValueError()
        conditionTmp = '@(' + edge + ' ' + signal + ');'
        self.commands.append({'wait': {'key': conditionTmp}})

    def add_transaction(self, transaction):
        self.commands.append(transaction)

    def add_transactions(self, transactions):
        for transaction in transactions:
            self.commands.append(transaction)

    def asdict(self):
        commands = []
        for command in self.commands:
            commands.append(command)
        return commands

if __name__ == "__main__":

    sonar = Sonar.default('sample')
    sonar.set_metadata('Module_Name', 'sample')

    dut = Module.default("DUT")
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
    test_vector_0.add_thread(initT)

    inputT = Thread()
    inputT.add_delay('100ns')
    inputT.init_timer()
    inputT.add_transaction(ctrl_bus.write('enable', 1))
    inputT.add_transaction(axis_in.write(tdata=0xABCD, callTB=2))
    inputT.wait_level('ack_V == $value', value=1)
    inputT.add_transaction(axis_in.write(tdata=0,callTB=3))
    inputT.wait_level('ack_V == $value', value=1)
    inputT.add_delay('110ns')
    inputT.set_flag(0)
    test_vector_0.add_thread(inputT)

    outputT = Thread()
    outputT.add_transaction(axis_out.read(tdata=1))
    outputT.wait_flag(0)
    outputT.add_transaction(ctrl_bus.read('enable', 1))
    outputT.print_elapsed_time('End')
    outputT.display('The_simulation_is_finished')
    outputT.end_vector()
    test_vector_0.add_thread(outputT)

    sonar.add_test_vector(test_vector_0)
    sonar.finalize_waits()

    # import pprint
    # sonar.asdict()
    # pprint.pprint(sonar.asdict())
    # print(sonar.asjson())

    sonar.generateTB('/home/sharm294/Documents/TMD/', 'sv')
    
