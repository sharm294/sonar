"""
Main module to define a testbench in sonar
"""

import json

import sonar.base_types as base
from sonar.core import generate


class Testbench(base.SonarObject):
    """
    Holds the complete testbench with global attributes, the modules, and the
    test vectors
    """

    def __init__(self):
        """
        Initializes a Testbench object with empty attributes
        """

        self.metadata = {}
        self.wait_conditions = []
        self.modules = {}
        self.vectors = []

    @classmethod
    def default(cls, module_name):
        """
        Initializes a Testbench with default metadata values

        Args:
            module_name (str): Name of the DUT module

        Returns:
            Testbench: the Testbench object represents the whole testbench
        """

        testbench = cls()
        testbench.metadata = {
            "Module_Name": module_name,
            "Timescale": "1ns / 1ps",
            "Time_Format": {"unit": "1us", "precision": 3},
            "Flag_Count": 1,
            "Timeout_Value": "10s",  # arbitrary large amount
            "Headers": [],
            "Company": None,
            "Engineer": None,
            "Project_Name": None,
            "Target_Devices": None,
            "Tool_Versions": None,
            "Description": None,
            "Dependencies": None,
        }
        return testbench

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
            raise KeyError("Key " + key + " already exists in metadata")
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
            raise KeyError("Key " + key + " does not exist in metadata")
        self.metadata[key] = value

    # def add_module(self, module):
    #     """
    #     Add a module to the testbench

    #     Args:
    #         module (Module): Module to add to this testbench
    #     """

    #     self.modules[module.name] = module

    def add_dut(self, module):
        """
        Add the device-under-test to the testbench

        Args:
            module (Module): Module to add to this testbench
        """

        module.name = "DUT"
        self.modules["DUT"] = module

    def add_test_vector(self, vector):
        """
        Add a test vector to the testbench

        Args:
            vector (TestVector): Vector containing one or more non-empty threads
        """

        self.vectors.append(vector)

    def _finalize_waits(self):
        """
        Using the test vectors in the testbench, this method aggregates all the
        wait conditions as required for the Sonar backend. This method must be
        called ONCE after all test vectors have been completed and added.
        """

        def update_waits(index, temp_key):
            if temp_key.isdigit():
                if int(temp_key) >= index:
                    raise Exception
                return None, index
            if temp_key not in conditions:
                new_key = str(index)
                waits.append({"condition": temp_key, "key": new_key})
                conditions.append(temp_key)
                index += 1
                return new_key, index
            for wait in waits:
                if wait["condition"] == temp_key:
                    key = wait["key"]
                    break
            return key, index

        waits = []
        conditions = []
        flag_present = False
        index = 0
        for vector in self.vectors:
            for thread in vector.threads:
                for command in thread.commands:
                    if "wait" in command:
                        temp_key = command["wait"]["key"]
                        if temp_key == "flag":
                            flag_present = True
                            continue
                        updated_key, index = update_waits(index, temp_key)
                        if updated_key:
                            command["wait"]["key"] = updated_key
        if flag_present:
            waits.append({"condition": "wait(flags[args[0]]);", "key": "flag"})
        self.wait_conditions = waits

    def asdict(self):
        """
        Converts the object to a dictionary

        Returns:
            dict: Dictionary representing the object
        """

        sonar_dict = {}
        sonar_dict["metadata"] = self.metadata
        modules = {}
        for _, module in self.modules.items():
            modules[module.name] = module.asdict()
        sonar_dict["modules"] = modules
        sonar_dict["wait_conditions"] = self.wait_conditions
        vectors = []
        for vector in self.vectors:
            vectors.append(vector.asdict())
        sonar_dict["vectors"] = vectors
        return sonar_dict

    def asjson(self):
        """
        Converts the testbench into JSON format for further processing or
        printing

        Returns:
            str: Testbench object dumped as JSON string
        """

        return json.dumps(self.asdict(), indent=2)

    def generate_tb(self, tb_filepath, languages, force=False):
        """
        After the Testbench object is complete, this will invoke the Sonar Core
        to generate the testbench(es) based on the information

        Args:
            tb_filepath (str): path to the sonar testbench script
            languages (str): sv or all to choose which languages
        """

        self._finalize_waits()
        generate.sonar(self, tb_filepath, languages, force)

    def get_from_dut(self, key):
        """
        Get certain parts of the DUT from the testbench

        Args:
            key (str): Key used to access different parts

        Returns:
            various: Return type depends on the key
        """
        dut = self.modules["DUT"]
        if key == "interfaces":
            return dut.ports.get_interfaces()
        if key == "interfaces_dict":
            return dut.ports.get_interfaces(collapse=False)
        if key == "signals":
            return dut.ports.get_signals()
        if key == "wait_conditions":
            return self.wait_conditions
        return getattr(dut, key)


class Module(base.SonarObject):
    """
    Defines a module in a testbench
    """

    def __init__(self):
        """
        Initializes a module with empty attributes
        """

        self.name = ""
        self.type = {"lang": "sv", "hls": None, "hls_version": None}
        self.ports = base.ModulePorts()
        self.parameters = []
        self.interfaces_count = {}

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

    @classmethod
    def cpp(cls, name, lang, hls, hls_version):
        """
        Creates a default cpp module with the given name, language and HLS tool

        Args:
            name (str): Name of the module to create
            lang (str): Language used for the module
            hls (str): HLS tool used to synthesize
            hls_version (str): HLS tool version

        Returns:
            Module: Object representing a module
        """

        module = cls()
        module.type["lang"] = lang
        module.type["hls"] = hls
        module.type["hls_version"] = hls_version
        module.name = name
        return module

    @classmethod
    def cpp_vivado(
        cls, name, clk_period="20ns", reset_low=True, version="2018.1"
    ):
        """
        Creates a default cpp module with the given name, language and HLS tool

        Args:
            name (str): Name of the module to create
            clk_period (str, optional): Defaults to 20ns. Clock period to use
            reset_low (bool, optional): Defaults to True. Enable active low reset
                Set False to use active high reset
            version (str, optional): Defaults to 2018.1. Vivado tool version

        Returns:
            Module: Object representing a module
        """

        module = cls().cpp(name, "cpp", "vivado", version)
        # assumes that all Vivado HLS IPs add a clock/reset with these names.
        # if this behavior changes, this needs to be updated
        module.add_clock_port("ap_clk", clk_period)
        if reset_low:
            module.add_reset_port("ap_rst_n")
        else:
            module.add_reset_port("ap_rst")
        return module

    def add_port(self, name, direction, size=1):
        """
        Adds a port to this module for a generic signal

        Args:
            name (str): Name of the signal
            direction (str): Must be one of (input|output)
            size (int, optional): Defaults to 1. Width of the port in bits
        """

        signal = base.SignalPort(name, size, direction)
        self.ports.add_signal(signal)

    def add_parameter(self, name, value):
        """
        Add a named parameter to this module's instantiation

        Args:
            name (str): Name of parameter
            value (str): Value to assign to parameter
        """
        self.parameters.append((name, value))

    def add_clock_port(self, name, period):
        """
        Adds an input clock port to this module (only for TB generated clocks)

        Args:
            name (str): Name of the clock signal
            period (str): Period of the clock (e.g. 20ns, 10ps etc.)
        """

        signal = base.ClockPort(name, 1, period, "input")
        self.ports.add_clock(signal)

    def add_reset_port(self, name):
        """
        Adds an input reset port to this module

        Args:
            name (str): Name of the reset signal
        """

        signal = base.SignalPort(name, 1, "input")
        self.ports.add_reset(signal)

    def add_interface(self, interface):
        """
        Adds an interface port to this module

        Args:
            interface (BaseInterface): Represents the interface port and
                must be a child class of BaseInterface.
        """

        port = interface
        if port.interface_type not in self.ports.interfaces.count:
            self.ports.interfaces.count[port.interface_type] = 0
        else:
            self.ports.interfaces.count[port.interface_type] += 1
        port.index = self.ports.interfaces.count[port.interface_type]
        port.readResp = "rresp_" + str(port.index)
        port.writeResp = "wresp_" + str(port.index)
        port.readData = "rdata_" + str(port.index)
        port.agent = "master_agent_" + str(port.index)
        self.ports.add_interface(port)

    def asdict(self):
        """
        Converts the object to a dictionary

        Returns:
            dict: Dictionary representing the object
        """
        module = {}
        module["name"] = self.name
        module["ports"] = self.ports.asdict()
        module["parameters"] = self.parameters
        module["type"] = self.type
        return module


class TestVector(base.SonarObject):
    """
    Defines a test vector in a testbench
    """

    def __init__(self, thread=None, threads=None):
        """
        Initializes a TestVector object

        Args:
            thread (Thread, optional): Defaults to None. An initial Thread to
                initialize with
            threads (Iterable of Threads, optional): Defaults to None. Initialize
                TestVector with all Threads in this iterable
        """

        self.threads = []
        if thread is not None:
            self.threads.append(thread)
        if threads is not None:
            for t in threads:
                self.threads.append(t)

    def add_thread(self, thread=None):
        """
        Adds a thread to the TestVector. If a thread is provided as an argument,
        it's added to the TestVector. Otherwise, an empty one is created, added
        and returned.

        Args:
            thread (Thread, optional): Defaults to None. The thread to add

        Returns:
            Thread: The added thread is returned
        """

        if thread is None:
            thread = Thread()
        self.threads.append(thread)
        return thread

    def asdict(self):
        """
        Converts the object to a dictionary

        Returns:
            dict: Dictionary representing the object
        """

        threads = []
        for thread in self.threads:
            threads.append(thread.asdict())
        return threads


class Thread(base.SonarObject):
    """
    Defines a one serial thread of execution in a parallel test vector
    """

    def __init__(self):
        """
        Initializes a default empty thread
        """

        self.commands = []
        self._enable_timestamps = False
        self.timestamp_prefix = ""
        self.timestamp_index = 0

    def add_delay(self, delay):
        """
        Add a timed delay to the thread

        Args:
            delay (str): String representing delay length e.g. '40ns'
        """

        self.commands.append({"delay": delay})
        self._print_timestamp()

    def set_signal(self, name, value):
        """
        Set the value of a signal to be the specified value

        Args:
            name (str): Name of the signal
            value (number): May be an int, or a hex or binary number string
                (preceded by 0x or 0b respectively)
        """

        self.commands.append({"signal": {"name": name, "value": value}})
        self._print_timestamp()

    def init_signals(self):
        """
        Initialize all signals to zero
        """

        self.commands.append({"macro": "INIT_SIGNALS"})

    def call_dut(self, num):
        """
        Call the DUT function some number of times (only for C++ TBs)

        Args:
            num (int): Number of times to call the DUT function
        """
        self.commands.append({"call_dut": num})

    def enable_timestamps(self, prefix, index):
        """
        Each subsequent command (until disabled) will print the time after it finishes
        with the given prefix and an index which starts at the provided one.

        Args:
            prefix (str): String to prefix the timestamp with
            index (int): Integer to start indexing the timestamps at
        """

        self._enable_timestamps = True
        self.timestamp_prefix = prefix
        self.timestamp_index = index
        self.commands.append({"timestamp": prefix + str(index)})
        self.timestamp_index += 1

    def disable_timestamps(self):
        """
        Disables timestamping
        """
        self._enable_timestamps = False

    def _print_timestamp(self):
        """
        Used internally to add a timestamping command after certain Thread commands
        """

        if self._enable_timestamps:
            self.commands.append(
                {
                    "timestamp": self.timestamp_prefix
                    + str(self.timestamp_index)
                }
            )
            self.timestamp_index += 1

    def init_timer(self):
        """
        Set the timer to zero to begin timestamping
        """

        self.commands.append({"timestamp": "INIT"})

    def print_elapsed_time(self, time_id):
        """
        Prints the elapsed time since the last init_timer command

        Args:
            id (str): String to print out with the timestamp for identification
        """

        self.commands.append({"timestamp": time_id})

    def print_time(self):
        """
        Prints the absolute time
        """

        self.commands.append({"timestamp": "PRINT"})

    def display(self, string):
        """
        Print the string to the console (note, must not contain spaces)

        Args:
            string (str): String to print
        """

        self.commands.append({"display": string})

    def end_vector(self):
        """
        Ends the TestVector. This command must be the last chronological event
        in the vector. If using C++ (or any other sequential simulation), the
        thread containing this command must also be the last thread in the
        vector
        """

        self.commands.append({"macro": "END"})
        self._print_timestamp()

    def set_flag(self, flag_id):
        """
        Set the flag with the given ID to 1. The number of flags available is
        set in the metadata of the testbench. Flags can be used to synchronize
        between threads. e.g. one thread can set a flag that another will wait
        for.

        Args:
            flag_id (number): ID of the flag to set (ranges from 0 to Flags-1)
        """

        self.commands.append({"flag": {"set_flag": flag_id}})
        self._print_timestamp()

    def wait_flag(self, flag_id):
        """
        Wait for the flag with the given ID to become 1. The number of flags
        available is set in the metadata of the testbench. Flags can be used to
        synchronize between threads. e.g. one thread can set a flag that another
        will wait for.

        Args:
            flag_id (number): ID of the flag to wait on (ranges from 0 to Flags-1)
        """

        self.commands.append({"wait": {"key": "flag", "args": [flag_id]}})
        self._print_timestamp()
        self.commands.append({"flag": {"clear_flag": flag_id}})

    def _statement(self, condition, *args):
        """
        Add a line to the thread, which is a complete Systemverilog line that
        that will be inserted verbatim into the TB. Any variables used in the
        statement will be replaced.

        Args:
            condition (str): SV-compatible statement (e.g. wait(); or @();)
            args (int): Conditions can use variables and their values can be
            passed in as args
        """

        self.commands.append({"wait": {"key": condition, "args": args}})
        self._print_timestamp()

    def wait_level(self, condition, *args):
        """
        Add a level-wait condition (wait until the signal value matches) to the
        thread.

        Args:
            condition (str): SV-compatible statement (e.g. 'signal == 1')
            args (int): Conditions can use 'args[x]' as variables and their
                values can be passed in as args
        """

        condition_tmp = "wait(" + condition + ");"
        self._statement(condition_tmp, *args)

    def assert_value(self, condition, *args):
        """
        Add an assertion condition (assert the signal value matches) to the
        thread.

        Args:
            condition (str): SV-compatible statement (e.g. 'signal == 1')
            args (int): Conditions can use 'args[x]' as variables and their
                values can be passed in as args
        """

        condition_tmp = "assert(" + condition + ");"
        self._statement(condition_tmp, *args)

    def wait_posedge(self, signal):
        """
        Add a positive-edge sensitive wait condition on a signal.

        Args:
            signal (str): Name of the signal to wait on
        """

        self._wait_edge("posedge", signal)

    def wait_negedge(self, signal):
        """
        Add a negative-edge sensitive wait condition on a signal.

        Args:
            signal (str): Name of the signal to wait on
        """

        self._wait_edge("negedge", signal)

    def _wait_edge(self, edge, signal):
        """
        Adds a edge sensitive wait condition on a signal

        Args:
            edge (str): posedge or negedge
            signal (str): Name of the signal to wait on

        Raises:
            ValueError: Raised if edge is not posedge or negedge
        """

        if edge not in ("posedge", "negedge"):
            raise ValueError()
        condition_tmp = "@(" + edge + " " + signal + ");"
        self._statement(condition_tmp)

    def _add_transaction(self, transaction):
        """
        Adds a valid transaction to the thread. Since this is raw, it is not
        recommended for user use.

        Args:
            transaction (object): Some object representing a transaction
        """

        self.commands.append(transaction)
        self._print_timestamp()

    def asdict(self):
        """
        Converts the object to a dictionary

        Returns:
            dict: Dictionary representing the object
        """

        commands = []
        for command in self.commands:
            commands.append(command)
        return commands
