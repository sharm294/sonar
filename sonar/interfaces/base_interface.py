"""
Defines the base interfaces classes that interfaces and interface cores
inherit from
"""
from __future__ import annotations

from typing import Dict

import sonar.base_types as base


def to_upper_case(signals):
    """
    For a dictionary of signals, change all the names to upper case

    Args:
        signals (dict): Dictionary of Signals

    Returns:
        dict: Updated dictionary
    """
    for _, signal in signals.items():
        signal.name = signal.name.upper()
    return signals


class InterfaceCore(base.SonarObject):
    """
    Defines the core properties of the interface that are used internally
    """

    signals: Dict[str, dict] = {}
    args: Dict[str, dict] = {}
    # text_replacements = None
    # write = None

    @staticmethod
    def import_packages_global():
        """
        Specifies any packages that must be imported once per testbench

        Returns:
            str: Packages to be imported
        """
        return ""

    @classmethod
    def write_sv(cls, packet):
        """
        Write one line of the SV data file

        Args:
            packet (dict): The command to write

        Returns:
            str: The command as a line for the data file
        """
        line = ""
        for word in packet["payload"]:
            count = 0
            line += packet["type"] + " " + packet["name"] + " $COUNT$"
            for arg, _ in cls.args["sv"].items():
                if arg in word:
                    count += 1
                    line += " " + str(word[arg])
            line = line.replace("$COUNT$", str(count))
            line += "\n"
        return line[:-1]

    @classmethod
    def write_cpp(cls, packet, identifier="NULL"):
        """
        Write one line of the C++ data file

        Args:
            packet (dict): The command to write

        Returns:
            str: The command as a line for the data file
        """
        line = ""
        for word in packet["payload"]:
            count = 0
            line += (
                packet["name"] + " " + "NULL" + " " + identifier + " $COUNT$"
            )
            for arg, _ in cls.args["cpp"].items():
                if arg in word:
                    count += 1
                    line += " " + str(word[arg])
            line = line.replace("$COUNT$", str(count))
            line += "\n"
        return line[:-1]

    @classmethod
    def asdict(cls):
        tmp = {}
        tmp["signals"] = cls.signals
        return tmp


class BaseInterface(base.SonarObject):
    """
    Defines an interface in sonar
    """

    def __init__(self, name, direction, core):
        """
        Initialize the BaseInterface class with an empty signal list

        Args:
            name (str): name of the interface
            direction (str): direction of the interface (master|slave|mixed)
            core (InterfaceCore): defines the low-level operation of the interface
        """
        self.name = name
        self.direction = direction
        self.signals = {}
        self.core = core
        self.endpoints = []
        self.interface_type = None

    @property
    def interfaceType(self):  # pylint: disable=invalid-name
        """
        This is used by regex for variable substitution so cannot have
        underscores

        Returns:
            str: type of this interface
        """
        return self.interface_type

    def add_signal(self, signal_type, signal):
        """
        Adds a signal to this interface

        Args:
            signal_type (str): Type of signal to add (interface-dependent)
            signal (Signal): Signal object
        """

        self.signals[signal_type] = signal

    def add_signals(self, signals):
        """
        Adds a set of signals to this interface port

        Args:
            signals (dict): signals to add to the interface
        """

        self.signals = {**self.signals, **signals}  # merge the two

    def get_signal(self, signal_type):
        """
        Returns information about the named signal on this interface

        Args:
            signal_type (str): The signal type to fetch

        Raises:
            KeyError: Raised if signal_type isn't found

        Returns:
            Signal: Information about the requested signal
        """

        return self.signals[signal_type]

    def has_signal(self, signal_type):
        """
        Returns a boolean if the interface has a specific signal

        Args:
            signal_type (str): The signal type to search

        Returns:
            bool: True if the interface has the signal
        """
        if signal_type in self.signals:
            return True
        return False

    def add_endpoint(self, endpoint, **kwargs):
        """
        Add an endpoint to the interface

        Args:
            endpoint (Endpoint): The endpoint to add
            kwargs (?): Keyworded arguments for the endpoint
        """
        endpoint.arguments = kwargs
        self.endpoints.append(endpoint)

    def asdict(self):
        tmp = {}
        tmp["name"] = self.name
        tmp["direction"] = self.direction
        tmp["core"] = self.core
        tmp["signals"] = {}
        for key, value in self.signals.items():
            tmp["signals"][key] = value.asdict()
        return tmp
