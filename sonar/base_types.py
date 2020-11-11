"""
This module defines basic object types used throughout sonar.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List, Tuple, Union

from sonar.exceptions import SonarInvalidArgError

if TYPE_CHECKING:
    import sonar.interfaces.base_interface as base

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


class InOutPorts(SonarObject):
    """
    Maintains a list of input and output signals
    """

    def __init__(self):
        self.input: List[SignalPort] = []
        self.output: List[SignalPort] = []

    def asdict(self):
        tmp = {"input": [], "output": []}
        for signal in self.input:
            tmp["input"].append(signal.asdict())
        for signal in self.output:
            tmp["output"].append(signal.asdict())
        return tmp


class InterfacePorts(SonarObject):
    """
    Maintains lists of the different interface directions
    """

    def __init__(self):
        self.master: List[base.BaseInterface] = []
        self.slave: List[base.BaseInterface] = []
        self.mixed: List[base.BaseInterface] = []
        self.count: Dict[str, int] = {}

    def asdict(self):
        tmp = {"master": [], "slave": [], "mixed": [], "count": self.count}
        for interface in self.master:
            tmp["master"].append(interface.asdict())
        for interface in self.slave:
            tmp["slave"].append(interface.asdict())
        for interface in self.mixed:
            tmp["mixed"].append(interface.asdict())
        return tmp


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


class ModulePorts:
    """
    Holds a module's ports
    """

    def __init__(self):
        self.clocks = InOutPorts()
        self.resets = InOutPorts()
        self.interfaces = InterfacePorts()
        self.signals = InOutPorts()

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
        module_ports["clocks"] = self.clocks.asdict()
        module_ports["resets"] = self.resets.asdict()
        module_ports["interfaces"] = self.interfaces.asdict()
        module_ports["signals"] = self.signals.asdict()
        return module_ports
