"""
Defines an AXI4-Lite Slave interface
"""

import itertools
import os

import sonar.base_types
import sonar.endpoints
import sonar.interfaces.base_interface as base


class AXI4LiteSlave(base.BaseInterface):
    """
    Defines the AXI-Lite slave interface
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, name, clock, reset):
        """
        Initialize an AXI4LiteSlave interface with the default options

        Args:
            name (str): Name of the AXI4-Lite interface
            clock (str): Name of associated clock
            reset (str): Name of associated reset
        """

        super().__init__(name, "mixed", AXI4LiteSlaveCore)
        if isinstance(clock, sonar.base_types.ClockPort):
            clock_name = clock.name
        else:
            clock_name = clock
        if isinstance(reset, sonar.base_types.SignalPort):
            reset_name = reset.name
        else:
            reset_name = reset
        self.clock = clock_name
        self.reset = reset_name
        self.resetBool = reset_name  # pylint: disable=invalid-name
        if self.reset.endswith("_n"):
            self.resetBool = "~" + self.resetBool
        self.registers = []
        self.addresses = []
        self.addr_range = ""
        self.addr_offset = ""
        self.interface_type = "axi4_lite_slave"

    @property
    def dataWidth(self):  # pylint: disable=invalid-name
        """
        This is used by regex for variable substitution so cannot have
        underscores

        Returns:
            int: Size of the data signal
        """
        return self.get_signal("wdata").size

    @property
    def addrWidth(self):  # pylint: disable=invalid-name
        """
        This is used by regex for variable substitution so cannot have
        underscores

        Returns:
            int: Size of the address signal
        """
        return self.get_signal("awaddr").size

    def add_endpoint(self, endpoint, **kwargs):
        """
        Add an endpoint to this AXI4-Lite interface

        Args:
            endpoint (str): Identifier for the endpoint
            kwargs (?): Keyworded arguments for the endpoint
        """
        endpoint_obj = None
        if endpoint == "manual":
            endpoint_obj = EndpointManual
        if endpoint_obj:
            super().add_endpoint(endpoint_obj, **kwargs)

    def write(self, thread, register, data):
        """
        Write data to a register

        Args:
            thread (Thread): Thread in which to write from
            register (str): Name of the register to write to
            data (number): Value that should be written
        """

        address = None
        for index, reg in enumerate(self.registers):
            if reg == register:
                address = self.addresses[index]
                break
        transaction = {
            "interface": {
                "type": "axi4_lite_slave",
                "name": self.name,
                "payload": [
                    {"endpoint_mode": 0, "data": data, "addr": address}
                ],
            }
        }
        thread._add_transaction(transaction)

    def read(self, thread, register, expected_value):
        """
        Read data from a register to verify its value

        Args:
            thread (Thread): Thread in which to read from
            register (str): Name of the register to read
            expected_value (number): Expected value that the register should have
        """

        address = None
        for index, reg in enumerate(self.registers):
            if reg == register:
                address = self.addresses[index]
                break
        transaction = {
            "interface": {
                "type": "axi4_lite_slave",
                "name": self.name,
                "payload": [
                    {
                        "endpoint_mode": 1,
                        "data": expected_value,
                        "addr": address,
                    }
                ],
            }
        }
        thread._add_transaction(transaction)

    def set_address(self, addr_range, addr_offset):
        """
        Sets the address range and offset for this AXI-Lite interface

        Args:
            addr_range (str): Address size e.g. '4K'
            addr_offset (number): Offset address
        """

        self.addr_range = addr_range
        self.addr_offset = addr_offset

    def add_register(self, name, address):
        """
        Add a register to this interface

        Args:
            name (str): Name of the register to add
            address (number): Address of the register
        """

        self.registers.append(name)
        self.addresses.append(address)

    def del_register(self, name):
        """
        Delete a register from this interface

        Args:
            name (str): Name of the register to delete
        """

        for index, name_ in enumerate(self.registers):
            if name_ == name:
                del self.registers[index]
                del self.addresses[index]
                break

    def init_signals(
        self, mode, data_width=None, addr_width=None, upper_case=True
    ):
        """
        Initialize the signals associated with this AXILite interface.
        Initialize means to specify the names, types and widths of all the
        signals.

        Args:
            mode (str): Name of a signal preset to use. Options are:
                'default': standard AXI-Lite without cache or prot
            data_width (number): Width of the data signal (r/w)
            addr_width (number): Width of the addr signal (r/w)
            upper_case (bool, optional): Defaults to True. Assume that
                the signal names are the uppercase versions of their type,
                which is the default for an HLS module. Setting it to False
                sets the name identical to the type (i.e. lowercase)

        Raises:
            NotImplementedError: Unhandled exception if bad mode entered
            ValueError: Error in mode/argument association
        """
        if mode == "default":
            if addr_width < 12:
                addr_width = (
                    12  # Minimum required by AXI standard for 4K memory
                )
            signals = {
                "awvalid": sonar.base_types.Signal("awvalid", 1),
                "awready": sonar.base_types.Signal("awready", 1),
                "awaddr": sonar.base_types.Signal("awaddr", addr_width),
                "wvalid": sonar.base_types.Signal("wvalid", 1),
                "wready": sonar.base_types.Signal("wready", 1),
                "wdata": sonar.base_types.Signal("wdata", data_width),
                "wstrb": sonar.base_types.Signal("wstrb", int(data_width / 8)),
                "arvalid": sonar.base_types.Signal("arvalid", 1),
                "arready": sonar.base_types.Signal("arready", 1),
                "araddr": sonar.base_types.Signal("araddr", addr_width),
                "rvalid": sonar.base_types.Signal("rvalid", 1),
                "rready": sonar.base_types.Signal("rready", 1),
                "rdata": sonar.base_types.Signal("rdata", data_width),
                "rresp": sonar.base_types.Signal("rresp", 2),
                "bvalid": sonar.base_types.Signal("bvalid", 1),
                "bready": sonar.base_types.Signal("bready", 1),
                "bresp": sonar.base_types.Signal("bresp", 2),
            }
        if upper_case:
            signals = base.to_upper_case(signals)
        self.add_signals(signals)

    def asdict(self):
        """
        Returns this object as a dictionary

        Returns:
            dict: The fields of this object as a dictionary
        """
        tmp = super().asdict()
        tmp["clock"] = self.clock
        tmp["reset"] = self.reset
        tmp["registers"] = self.registers
        tmp["addresses"] = self.addresses
        tmp["addr_offset"] = self.addr_offset
        tmp["addr_range"] = self.addr_range

        return tmp


class AXI4LiteSlaveCore(base.InterfaceCore):
    """
    Defines the core properties of the AXI4-Lite Slave interface used internally
    """

    signals = {
        "input": {
            "awready": {"size": 1, "required": True},
            "wready": {"size": 1, "required": True},
            "arready": {"size": 1, "required": True},
            "rvalid": {"size": 1, "required": True},
            "rdata": {"size": 0, "required": True},
            "rresp": {"size": 2, "required": True},
            "bvalid": {"size": 1, "required": True},
            "bresp": {"size": 2, "required": True},
        },
        "output": {
            "awvalid": {"size": 1, "required": True},
            "awaddr": {"size": 0, "required": True},
            "wvalid": {"size": 1, "required": True},
            "wdata": {"size": 0, "required": True},
            "wstrb": {"size": 0, "required": True},
            "arvalid": {"size": 1, "required": True},
            "araddr": {"size": 0, "required": True},
            "rready": {"size": 1, "required": True},
            "bready": {"size": 1, "required": True},
        },
    }

    args = {
        "sv": {
            "endpoint_mode": 0,
            "addr": 1,
            "data": 2,
        },
        "cpp": {
            "addr": 0,
            "data": 1,
        },
    }

    @staticmethod
    def import_packages_global():
        """
        Specifies any packages that must be imported once per testbench

        Returns:
            str: Packages to be imported
        """
        imports = ""

        # versionInfo = subprocess.check_output("vivado -version", shell=True)
        version = os.getenv("SONAR_CAD_VERSION")
        # version = versionInfo.split()[1].decode("utf-8")

        if version == "2017.2":
            imports += "import axi_vip_v1_0_2_pkg::*;\n"
        else:
            imports += "import axi_vip_pkg::*;\n"
        return imports


class EndpointManual(sonar.endpoints.InterfaceEndpoint):
    """
    Manual endpoint
    """

    actions = {
        "sv": {
            "write": [
                "$$agent.AXI4LITE_WRITE_BURST(args[1],0,args[2],$$writeResp);"
            ],
            "read": [
                "$$agent.AXI4LITE_READ_BURST(args[1],0,$$readData,$$readResp); //addr, prot, read_data, resp",
                "assert($$readData == args[2]) begin",
                "end else begin",
                '    $error("S-AXILITE Assert failed at %t on $$readData. Expected: %h, Received: %h", $time, args[2], $$readData);',
                "    retval = 1;",
                "end",
            ],
        },
        "cpp": {
            "master": [
                {
                    "foreach": "registers",
                    "commands": [
                        "if(args[0] == $$addresses){",
                        "    $$registers = args[1];",
                        "}",
                    ],
                },
            ],
            "slave": [],
        },
    }

    @staticmethod
    def import_packages_local(interface):
        """
        Specifies any packages that must be imported once per interface

        Args:
            interface (AXI4LiteSlave): AXI4LiteSlave instance

        Returns:
            str: Packages to be imported
        """
        return (
            "import vip_bd_" + str(interface.index) + "_axi_vip_0_0_pkg::*;\n"
        )

    @staticmethod
    def initial_blocks(indent):
        """
        Any text that should be inside an initial block

        Args:
            indent (str): Indentation to add to each line

        Returns:
            list[str]: List of strings that go into separate initial blocks
        """
        prologue = (
            indent
            + '$$agent = new("master vip agent", vip_bd_$$index_i.axi_vip_0.inst.IF);\n'
        )
        prologue += indent + '$$agent.set_agent_tag("$$agent");\n'
        prologue += indent + "$$agent.start_master();\n"
        return [prologue]

    @staticmethod
    def prologue(indent):
        """
        Any text that should be part of the testbench as a prologue outside any
        blocks such as variable declarations.

        Args:
            indent (str): Indentation to add to each line

        Returns:
            str: Updated prologue
        """
        prologue = indent + "logic [$$dataWidth-1:0] rdata_$$index;\n"
        prologue += indent + "xil_axi_resp_t rresp_$$index;\n"
        prologue += indent + "xil_axi_resp_t wresp_$$index;\n"
        prologue += (
            indent + "vip_bd_$$index_axi_vip_0_0_mst_t master_agent_$$index;\n"
        )
        return prologue

    @staticmethod
    def source_tcl(interface, path):
        """
        Any TCL files that should be sourced as part of initializing the
        interface

        Args:
            interface (AXI4LiteSlave): AXI4LiteSlave object
            path (str): Path where to place the TCL source files
        """

        tcl_file_name = os.path.join(
            os.path.dirname(__file__), "axi4_lite_slave_vip.tcl"
        )
        with open(tcl_file_name) as f:
            tcl_file = f.read()
            tcl_file = tcl_file.replace(
                "#DESIGN_NAME#", "vip_bd_" + str(interface.index)
            )
            tcl_file = tcl_file.replace(
                "#ADDR_WIDTH#", str(interface.addrWidth)
            )
            tcl_file = tcl_file.replace(
                "#DATA_WIDTH#", str(interface.dataWidth)
            )
            tcl_file = tcl_file.replace("#ADDRESS#", str(interface.addr_range))
            tcl_file = tcl_file.replace(
                "#ADDRESS_OFFSET#", str(interface.addr_offset)
            )
            tcl_file_gen = open(
                os.path.join(
                    path,
                    "axi4_lite_slave_vip_" + str(interface.index) + ".tcl",
                ),
                "w+",
            )
            tcl_file_gen.write(tcl_file)
            tcl_file_gen.close()

    @staticmethod
    def instantiate(indent):
        """
        Any modules that this interface instantiates in SV.

        Args:
            interface (AXI4LiteSlave): AXI4LiteSlave
            indent (str): Indentation to add to each line

        Returns:
            str: Updated ip_inst
        """
        index = "$$endpointIndex"
        one_tab = indent + "    "
        ip_inst = indent
        ip_inst += "vip_bd_" + index + " vip_bd_" + index + "_i(\n"
        ip_inst += one_tab + ".aclk($$clock),\n"
        ip_inst += one_tab + ".aresetn($$reset),\n"
        for signal_type in itertools.chain(
            AXI4LiteSlaveCore.signals["input"],
            AXI4LiteSlaveCore.signals["output"],
        ):

            ip_inst += one_tab + ".m_axi_" + signal_type + "(" + "$$name" + "_"
            if signal_type in AXI4LiteSlaveCore.signals["output"]:
                ip_inst += signal_type + "_endpoint[$$endpointIndex]" + "),\n"
            else:
                ip_inst += signal_type + "),\n"
        ip_inst = ip_inst[:-2] + "\n" + indent + ");\n"
        return ip_inst
