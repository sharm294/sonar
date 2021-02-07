"""
Signal endpoints that can be used in testbenches
"""

from typing import Dict

import sonar.base_types as base


class Endpoint(base.SonarObject):
    """
    Endpoint class
    """

    actions: Dict[str, Dict] = {}
    arguments: Dict[str, int] = {}

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

    @staticmethod
    def instantiate(_indent, _tab_size):
        """
        Any modules that this interface instantiates in SV.

        Args:
            indent (str): Indentation to add to each line
            tab_size (str): One tab worth of indent

        Returns:
            str: Updated ip_inst
        """
        return ""

    @classmethod
    def asdict(cls):
        tmp = {
            "import_packages_local": False,
            "initial_blocks": False,
            "source_tcl": False,
            "prologue": False,
            "instantiate": False,
        }
        return tmp
