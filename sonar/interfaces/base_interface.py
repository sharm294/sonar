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
    actions: Dict[str, dict] = {}
    args: Dict[str, dict] = {}
    # text_replacements = None
    # write = None

    @classmethod
    def asdict(cls):
        tmp = {}
        tmp["signals"] = cls.signals
        tmp["actions"] = cls.actions
        tmp["args"] = cls.args
        # tmp["text_replacements"] = cls.text_replacements
        # tmp["write"] = cls.write
        return tmp

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


class BaseInterface(base.SonarObject):
    """
    Defines an interface in sonar
    """

    def __init__(self, name, direction, core, connnection_mode="native"):
        """
        Initialize the BaseInterface class with an empty signal list

        Args:
            name (str): name of the interface
            direction (str): direction of the interface (master|slave|mixed)
            core (InterfaceCore): defines the low-level operation of the interface
            connection_mode (str): defines the connection type to the interface
        """
        self.name = name
        self.direction = direction
        self.signals = {}
        self.index = 0
        self.connection_mode = connnection_mode
        self.core = core
        self.interface_type = None

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

    def asdict(self):
        tmp = {}
        tmp["name"] = self.name
        tmp["direction"] = self.direction
        tmp["signals"] = self.signals
        tmp["index"] = self.index
        tmp["connection_mode"] = self.connection_mode
        tmp["interface_type"] = self.interface_type
        return tmp
