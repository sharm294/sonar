# sonar

*sonar* is an automated simulation and testbenching infrastructure for hardware. The only user input required is a YAML configuration file which defines the ports of the device-under-test (DUT), test vectors, and optionally, a set of wait conditions. With the configuration file, *sonar* will generate a .sv testbench and an associated .dat file containing the user specified test vectors. A C-sim testbench file is not currently being auto-generated though a .dat file for it is being created.

All generated files are placed in a newly created ./build/ directory relative to the path of the configuration file.

## Usage
``source init.sh`` with the correct arguments (run without args for help) to initialize repository. Then use the appropriate make commands or run scripts as needed. ``make sample`` and ``make hw`` will generate all the needed files to import into a Vivado project. The top-level script to run manually is *sonar.py*.

## Sample
These are the files included in ``sample/``:  
* ``sample.cpp``: HLS DUT
* ``sample.hpp``: header for ``sample.cpp``
* ``sample.yaml``: example user configuration file
* ``sample.sh``: creates the HLS project by calling ``sample.tcl``
* ``sample.tcl``: creates an HLS project for ``sample.cpp``

A Vivado project for sample can be created by adding the .v file from HLS and the systemverilog testbench + sample_sv.dat from build/ to the project. Add the sonar include/ directory as a search path in the project under Settings/general/Verilog options

## Dependencies

Vivado and Vivado HLS are assumed to be on the PATH. The scripts have been tested on Bash, with Python 2.7 and Vivado 2017.2 on Ubuntu 16.04. Two environment variables are also added: SONAR_VIVADO_HLS and SONAR_PATH. The package python-yaml is installed during initialization

## Caveats

There are a number of things on the todo list to implement such as code cleanup, new functionality, and improving comments. Testing has also not been rigorous so there may (read: probably) be corner cases which are not being correctly handled and will be fixed when observed.
