import json
import math
import os
import sys

from .base_types import SonarObject, InterfacePort
from .core import sonar as SonarCore


class Testbench(SonarObject):
    def __init__(self):
        """
        Initializes a Testbench object with empty attributes
        """

        self.metadata = {}
        self.wait_conditions = []
        self.modules = []
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

    def _finalize_waits(self):
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
                    if "wait" in command:
                        # print(command)
                        tempKey = command["wait"]["key"]
                        # print(tempKey)
                        if tempKey == "flag":
                            flagPresent = True
                            continue
                        if tempKey.isdigit():
                            if int(tempKey) >= index:
                                raise Exception
                            continue
                        if tempKey not in conditions:
                            newKey = str(index)
                            waits.append({"condition": tempKey, "key": newKey})
                            conditions.append(tempKey)
                            index += 1
                            command["wait"]["key"] = newKey
                        else:
                            for wait in waits:
                                if wait["condition"] == tempKey:
                                    key = wait["key"]
                                    break
                            command["wait"]["key"] = key
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
        sonar_dict["metadata"] = self.metadata
        modules = []
        for module in self.modules:
            modules.append(module.asdict())
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

    def generateTB(self, directory_path, languages):
        """
        After the Testbench object is complete, this will invoke the Sonar Core
        to generate the testbench(es) based on the information

        Args:
            directory_path (str): path to store the generated files
            languages (str): sv or all to choose which languages
        """

        self._finalize_waits()
        filename = self.metadata["Module_Name"]
        filepath = directory_path + filename + ".json"
        try:
            os.makedirs(directory_path, 0o775)
        except OSError:
            if not os.path.isdir(directory_path):
                raise
        with open(filepath, "w+") as f:
            json.dump(self.asdict(), f, indent=2)
        SonarCore.sonar("absolute", None, filepath, languages)


class Module(SonarObject):
    def __init__(self):
        """
        Initializes a module with empty attributes
        """

        self.name = ""
        self.ports = []
        self.parameters = {}

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
        port["name"] = name
        port["size"] = size
        port["direction"] = direction
        self.ports.append(port)

    def add_parameter(self, name, value):
        """
        Add a named parameter to this module's instantiation

        Args:
            name (str): Name of parameter
            value (str): Value to assign to parameter
        """
        self.parameters[name] = value

    def add_clock_port(self, name, period):
        """
        Adds an input clock port to this module (only for TB generated clocks)

        Args:
            name (str): Name of the clock signal
            period (str): Period of the clock (e.g. 20ns, 10ps etc.)
        """

        port = {}
        port["name"] = name
        port["size"] = 1
        port["type"] = "clock"
        port["period"] = period
        port["direction"] = "input"
        self.ports.append(port)

    def add_reset_port(self, name):
        """
        Adds an input reset port to this module

        Args:
            name (str): Name of the reset signal
        """

        port = {}
        port["name"] = name
        port["size"] = 1
        port["type"] = "reset"
        port["direction"] = "input"
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
        module["name"] = self.name
        module["ports"] = []
        for port in self.ports:
            if isinstance(port, InterfacePort):
                module["ports"].append(port.asdict())
            else:
                module["ports"].append(port)
        module["parameters"] = self.parameters
        return module


class TestVector(SonarObject):
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


class Thread(SonarObject):
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

        self.commands.append({"signal": [{"name": name, "value": value}]})
        self._print_timestamp()

    def init_signals(self):
        """
        Initialize all signals to zero
        """

        self.commands.append({"macro": "INIT_SIGNALS"})

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
                {"timestamp": self.timestamp_prefix + str(self.timestamp_index)}
            )
            self.timestamp_index += 1

    def init_timer(self):
        """
        Set the timer to zero to begin timestamping
        """

        self.commands.append({"timestamp": "INIT"})

    def print_elapsed_time(self, id):
        """
        Prints the elapsed time since the last init_timer command

        Args:
            id (str): String to print out with the timestamp for identification
        """

        self.commands.append({"timestamp": id})

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

    def set_flag(self, id):
        """
        Set the flag with the given ID to 1. The number of flags available is
        set in the metadata of the testbench. Flags can be used to synchronize
        between threads. e.g. one thread can set a flag that another will wait
        for.

        Args:
            id (number): ID of the flag to set (ranges from 0 to Flags-1)
        """

        self.commands.append({"flag": {"set_flag": id}})
        self._print_timestamp()

    def wait_flag(self, id):
        """
        Wait for the flag with the given ID to become 1. The number of flags
        available is set in the metadata of the testbench. Flags can be used to
        synchronize between threads. e.g. one thread can set a flag that another
        will wait for.

        Args:
            id (number): ID of the flag to wait on (ranges from 0 to Flags-1)
        """

        self.commands.append({"wait": {"key": "flag", "value": id}})
        self._print_timestamp()
        self.commands.append({"flag": {"clear_flag": id}})

    def wait(self, condition, value=None):
        """
        Add a wait condition to the thread. For now, the condition must be a
        complete SystemVerilog line that will be inserted verbatim into the TB.
        The terminating semicolon should be included.

        Args:
            condition (str): SV-compatible wait statement (e.g. wait(); or @();)
            value (number, optional): Defaults to None. The condition can use
                '$value' as a variable and pass the number that should be
                inserted. e.g. wait(signal == $value)
        """

        if value is None:
            self.commands.append({"wait": {"key": condition}})
        else:
            self.commands.append({"wait": {"key": condition, "value": value}})
        self._print_timestamp()

    def wait_level(self, condition, value=None):
        """
        Add a level-wait condition (wait until the signal value matches) to the
        thread.

        Args:
            condition (str): SV-compatible statement (e.g. 'signal == 1')
            value (number, optional): Defaults to None. The condition can use
                '$value' as a variable and pass the number that should be
                inserted. e.g. 'signal == $value'
        """

        conditionTmp = "wait(" + condition + ");"
        if value is None:
            self.commands.append({"wait": {"key": conditionTmp}})
        else:
            self.commands.append({"wait": {"key": conditionTmp, "value": value}})
        self._print_timestamp()

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

        if edge != "posedge" and edge != "negedge":
            raise ValueError()
        conditionTmp = "@(" + edge + " " + signal + ");"
        self.commands.append({"wait": {"key": conditionTmp}})
        self._print_timestamp()

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
