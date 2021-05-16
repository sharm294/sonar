"""
Signal endpoints that can be used in testbenches
"""

import textwrap
from typing import Dict

import sonar.base_types as base


class Endpoint(base.SonarObject):
    """
    Endpoint class
    """

    arguments: Dict[str, int] = {}

    @classmethod
    def instantiate(cls, _indent):
        """
        Instantiate the endpoint logic

        Args:
            _indent (str): Indentation to add to each line

        Returns:
            str: Updated ip_inst
        """
        return ""

    @classmethod
    def asdict(cls):
        tmp = {
            "instantiate": False,
        }
        return tmp


class InterfaceEndpoint(Endpoint):
    """
    InterfaceEndpoints class
    """

    actions: Dict[str, Dict] = {}

    @staticmethod
    def import_packages_local(_interface):
        """
        Specifies any packages that must be imported once per endpoint

        Args:
            interface (Interface): The interface belonging to the endpoint

        Returns:
            str: Packages to be imported
        """
        return ""

    @staticmethod
    def initial_blocks(_indent):
        """
        Any text that should be inside an initial block

        Args:
            indent (str): Indentation to add to each line

        Returns:
            list[str]: List of strings that go into separate initial blocks
        """
        return []

    @staticmethod
    def prologue(_indent):
        """
        Any text that should be part of the testbench as a prologue outside any
        blocks such as variable declarations.

        Args:
            prologue (str): The preceding text to append to
            indent (str): Indentation to add to each line

        Returns:
            str: Updated prologue
        """
        return ""

    @staticmethod
    def source_tcl(_interface, _path):
        """
        Any TCL files that should be sourced as part of initializing the
        interface

        Args:
            interface (AXI4LiteSlave): AXI4LiteSlave object
            path (str): Path where to place the TCL source files
        """
        return None

    @classmethod
    def asdict(cls):
        tmp = super().asdict()
        tmp["import_packages_local"] = False
        tmp["initial_blocks"] = False
        tmp["source_tcl"] = False
        tmp["prologue"] = False
        return tmp


class PeriodicSignal(Endpoint):
    """
    Endpoint class
    """

    @classmethod
    def instantiate(cls, indent):
        """
        Any modules that this interface instantiates in SV.

        Args:
            indent (str): Indentation to add to each line

        Returns:
            str: Updated ip_inst
        """
        name = cls.arguments["name"]
        initial_value = cls.arguments["value"]
        period = cls.arguments["period"]
        block = textwrap.indent(
            textwrap.dedent(
                f"""\
            initial begin
                {name}_endpoint[$$endpointIndex] = {initial_value};
                forever begin
                    #({period}/2) {name}_endpoint[$$endpointIndex] <= ~{name}_endpoint[$$endpointIndex];
                end
            end
            """
            ),
            indent,
        )
        return block

    @classmethod
    def asdict(cls):
        tmp = {
            "instantiate": False,
        }
        return tmp
