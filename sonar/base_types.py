"""
This module defines basic object types used throughout sonar.
"""
from __future__ import annotations

import logging
from collections import namedtuple
from typing import Tuple, Union

from sonar.exceptions import SonarInvalidArgError

logger = logging.getLogger(__name__)


class SonarObject:
    """
    The basic object. It enforces that the object has a method to turn itself
    into a dictionary (for easy printing).
    """

    __test__ = False  # prevent pytest from picking up these objects

    def __str__(self):
        """
        Prints the object as a string

        Returns:
            str: Object as a string
        """

        return str(self.asdict())

    def asdict(self):
        """
        Placeholder function that's overridden in the child classes

        Raises:
            NotImplementedError: This function should not be called
        """

        raise NotImplementedError


class InterfacePort(SonarObject):
    """
    Used to define an interface port on a hardware module
    """

    def __init__(self, name, direction):
        """
        Initializes the parent InterfacePort class with an empty channel list

        Args:
            name (str): name of the interface
            direction (str): direction of the interface (master|slave|mixed)
        """

        self.name = name
        self.direction = direction
        self.channels = []
        self.index = 0  # should be overwritten eventually

    def add_channel(self, name, channel_type, size=1):
        """
        Adds a channel to this interface port

        Args:
            name (str): Name of the channel signal
            channel_type (str): Type of channel
            size (int, optional): Defaults to 1. Width of channel in bits
        """

        channel = {}
        channel["name"] = name
        channel["type"] = channel_type
        channel["size"] = size
        self.channels.append(channel)

    def add_channels(self, channels):
        """
        Adds a set of channels to this interface port

        Args:
            channels (list): List of channels to add to the interface. Each
                element in the list may be a list or a dict. If it's a list,
                the name, channel_type, and (optionally) size must appear in
                this order. If it's a dict, these arguments must be keyworded.

        Raises:
            NotImplementedError: Raised on unhandled errors
        """

        for channel in channels:
            if isinstance(channel, list):
                name = channel[0]
                channel_type = channel[1]
                if len(channel) == 3:
                    size = channel[2]
                else:
                    size = 1
            elif isinstance(channel, dict):
                name = channel["name"]
                channel_type = channel["type"]
                if "size" in channel:
                    size = channel["size"]
                else:
                    size = 1
            else:
                raise NotImplementedError()
            self.add_channel(name, channel_type, size)

    def get_channel(self, channel_type):
        """
        Returns information about the named channel on this interface

        Args:
            channel_type (str): The channel type to fetch

        Raises:
            KeyError: Raised if channel_type isn't found

        Returns:
            dict: Information about the requested channel
        """

        channel_dict = None
        for channel in self.channels:
            if channel["type"] == channel_type:
                channel_dict = channel
                break
        if channel_dict is None:
            raise KeyError()
        return channel_dict

    def has_channel(self, channel_type):
        """
        Returns a boolean value if the interface has the specific channel

        Args:
            channel_type (str): The channel type to fetch

        Returns:
            boolean: True if the channel exists in the interface
        """

        channel_exists = False
        for channel in self.channels:
            if channel["type"] == channel_type:
                channel_exists = True
                break
        return channel_exists

    def asdict(self):
        """
        Converts this object to a dictionary

        Returns:
            dict: Dictionary representing this object
        """
        port = {}
        port["name"] = self.name
        port["direction"] = self.direction
        port["channels"] = self.channels
        port["index"] = self.index
        return port


InOutPorts = namedtuple("InOutPort", ["input", "output"])
InterfacePorts = namedtuple(
    "InterfacePorts", ["master", "slave", "mixed", "count"]
)


class Signal(SonarObject):
    """
    Defines a signal
    """

    def __init__(self, name, size):
        self.name = name
        self.size = size

    def asdict(self):
        tmp = {}
        tmp["name"] = self.name
        tmp["size"] = self.size
        return tmp


class Clock(Signal):
    """
    Defines a clock
    """

    def __init__(self, name, size, period):
        super().__init__(name, size)
        self.period = period

    def asdict(self):
        tmp = super().asdict()
        tmp["period"] = self.period
        return tmp


class SignalPort(Signal):
    """
    Defines a signal port on a module
    """

    def __init__(self, name, size, direction):
        super().__init__(name, size)
        self.direction = direction

    def asdict(self):
        tmp = super().asdict()
        tmp["direction"] = self.direction
        return tmp


class ClockPort(Clock):
    """
    Defines a clock port on a module
    """

    def __init__(self, name, size, period, direction):
        super().__init__(name, size, period)
        self.direction = direction

    def asdict(self):
        tmp = super().asdict()
        tmp["direction"] = self.direction
        return tmp


# Signal = namedtuple("Signal", ["name", "size", "direction"])
# Clock = namedtuple("Clock", ["name", "size", "direction", "period"])


class ModulePorts:
    """
    Holds a module's ports
    """

    def __init__(self):
        self.clocks = InOutPorts([], [])
        self.resets = InOutPorts([], [])
        self.interfaces = InterfacePorts([], [], [], {})
        self.signals = InOutPorts([], [])

    def _get_ports(
        self,
        attribute: str,
        directions: Union[str, tuple, list],
        collapse: bool,
    ) -> Union[list, dict]:
        """
        Return some subset of the ports of the module based on the attribute and
        directions.

        Args:
            attribute (str): Type of port to get
            directions (Union[str, tuple, list]): Direction(s) of the port type
                to get
            collapse (bool): Collapse all ports into a list if true or return as
                a dict where the direction is the key

        Raises:
            SonarInvalidArgError: Raised if a direction is passed as a string and
                the port type or direction does not exist.

        Returns:
            Union[list, dict]: The retrieved ports of the module
        """
        if isinstance(directions, str):
            try:
                ports = getattr(getattr(self, attribute), directions)
            except KeyError as ex:
                raise SonarInvalidArgError from ex
            return ports
        if collapse:
            ports = []
        else:
            ports = {}
        for direction in directions:
            try:
                ports_subset = getattr(getattr(self, attribute), direction)
            except KeyError:
                logger.warning(
                    "Direction %s not found in %s, skipping.",
                    direction,
                    attribute,
                )
            else:
                if collapse:
                    ports.extend(ports_subset)
                else:
                    ports[direction] = ports_subset
        return ports

    def _add_ports(self, attribute: str, signal) -> None:
        getattr(getattr(self, attribute), signal.direction).append(signal)

    def get_clocks(
        self,
        directions: Tuple[str, str] = ("input", "output"),
        collapse: bool = True,
    ):
        """
        Get the module's clocks

        Args:
            directions (tuple, optional): Clock directions to get. Defaults to
                ("input", "output").
            collapse (bool, optional): Return one list with all clocks if true
            or return a dict whose indices are the directions. Defaults to True.

        Returns:
            Union[list, dict]: Module clocks
        """
        return self._get_ports("clocks", directions, collapse)

    def get_resets(self, directions=("input", "output"), collapse=True):
        """
        Get the module's resets

        Args:
            directions (tuple, optional): Reset directions to get. Defaults to
                ("input", "output").
            collapse (bool, optional): Return one list with all resets if true
            or return a dict whose indices are the directions. Defaults to True.

        Returns:
            Union[list, dict]: Module resets
        """
        return self._get_ports("resets", directions, collapse)

    def get_interfaces(
        self, directions=("master", "slave", "mixed"), collapse=True
    ):
        """
        Get the module's interfaces

        Args:
            directions (tuple, optional): Reset directions to get. Defaults to
                ("master", "slave", "mixed").
            collapse (bool, optional): Return one list with all interfaces if true
            or return a dict whose indices are the directions. Defaults to True.

        Returns:
            Union[list, dict]: Module interfaces
        """
        return self._get_ports("interfaces", directions, collapse)

    def get_signals(self, directions=("input", "output"), collapse=True):
        """
        Get the module's signals (excludes clocks, resets, and signals that are
        a part of interfaces).

        Args:
            directions (tuple, optional): Signal directions to get. Defaults to
                ("input", "output").
            collapse (bool, optional): Return one list with all signals if true
            or return a dict whose indices are the directions. Defaults to True.

        Returns:
            Union[list, dict]: Module signals
        """
        return self._get_ports("signals", directions, collapse)

    def add_signal(self, signal):
        """
        Add a signal to the module

        Args:
            signal (SignalPort): A SignalPort object
        """
        self._add_ports("signals", signal)

    def add_reset(self, signal):
        """
        Add a reset to the module

        Args:
            signal (SignalPort): A SignalPort object
        """
        self._add_ports("resets", signal)

    def add_clock(self, signal):
        """
        Add a clock to the module

        Args:
            signal (ClockPort): A ClockPort object
        """
        self._add_ports("clocks", signal)

    def add_interface(self, interface):
        """
        Add an interface to the module

        Args:
            interface (BaseInterface): An interface
        """
        self._add_ports("interfaces", interface)

    def __str__(self):
        return (
            str(self.clocks)
            + "\n"
            + str(self.resets)
            + "\n"
            + str(self.signals)
        )

    def asdict(self):
        """
        Return the Module ports object as a dict

        Returns:
            dict: Module ports
        """
        module_ports = {}
        module_ports["clocks"] = self.clocks
        module_ports["resets"] = self.resets
        # TODO interfaces can't be printed
        # module_ports["interfaces"] = self.interfaces
        module_ports["signals"] = self.signals
        return module_ports
