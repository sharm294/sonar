***************
Version History
***************

3.x
===

3.1.0dev
--------

In progress

Features
^^^^^^^^

- Add parameters for SV DUTs
- Add global timeout for SV testbenches
- Add user-specified header files for testbenches
- Improve C++ testbenches
    - Better SV-like testbench generation as opposed to relying on user macros
    - New ``call_dut()`` command for Threads (ignored in SV testbenches)
    - Remove ``callTB`` as an interface argument
    - Replace ``c_stream`` and ``c_struct`` with ``iClass`` (interface class)
      and ``flit``, respectively
- Add ``cpp_vivado`` constructor for Modules

Bugfixes
^^^^^^^^

Changes
^^^^^^^

C++ testbench generation
""""""""""""""""""""""""

This update breaks old Sonar testbenches for C++ testbench generation. To
correctly generate C++ testbenches:
- use the ``cpp_vivado`` constructor for modules (used to mark the source file
  as a C++ source for Vivado HLS which is used for some assumptions about DUT
  signals)
- omit the clock and reset signals (added automatically based on cpp_vivado
  constructor)
- remove the "_V" suffix on signal names (added automatically based on cpp_vivado
  constructor)
- add any header files that may be needed explicitly (a C++ header file is no
  longer inferred to exist with the same name as the module)
- update the ``c_stream`` and ``c_struct`` tags to ``iClass`` and ``flit``,
  respectively (these refer to the AXIS interface type [this may be
  ``hls::stream<flit_t>`` or some other ``typedef`` user class] and the AXIS flit
  type [this should be the type of ``struct`` used in the AXIS with fields for
  ``tdata`` and other AXIS signals as needed], respectively)
- add the ``call_tb`` as needed to call the DUT function

The data file format and testbench template for C++ has also changed and so
testbenches need to be regenerated from Sonar.

3.0.0
-----

Released June 12, 2020

- Initial modern release
