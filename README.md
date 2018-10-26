# sonar

*sonar* is an automated simulation and testbenching infrastructure for
hardware. The only user input required is a YAML configuration file which
defines the ports of the device-under-test (DUT), test vectors, and optionally,
a set of wait conditions. With the configuration file, *sonar* will generate a
.sv testbench and an associated .dat file containing the user specified test
vectors. It will also generate a C++ data file + testbench though that is not 
quite as sophisticated.

All generated files are placed in a newly created ./build/ directory relative
to the path of the configuration file.

## Usage
``source init.sh`` with the correct arguments (run without args for help) to
initialize repository first. Provide the absolute path to the cloned repository 
and, optionally, the path to the Vivado HLS include folder (usually 
Xilinx/Vivado_HLS/\<year\>/include). Remove any trailing slashes from the path. 
Then use the make commands to create the sample or run scripts on your own 
designs. 

To create the sample project, run ``make sample``. This will create a Vivado 
HLS project, generate all the testbenches and data files and open Vivado for 
simulation.

If running manually, the top-level script to run is *sonar.py*.

## Sample
These are the files included in ``sample/``:  
* ``sample.cpp``: HLS DUT
* ``sample.hpp``: header for ``sample.cpp``
* ``sample.yaml``: example user configuration file
* ``sample.sh``: creates the HLS project by calling ``sample.tcl``
* ``sample_hls.tcl``: creates an HLS project for ``sample.cpp``
* ``sample_vivado.tcl``: creates a Vivado project for simulating the generated
testbench

## Dependencies

Vivado and Vivado HLS are assumed to be on the PATH. The scripts have been
tested on Bash, with Python 2.7 and Vivado 2017.2 on Ubuntu 16.04. Two
environment variables are also added: SONAR_VIVADO_HLS and SONAR_PATH. The
package python-yaml is also required (it may be called something different on 
your distro. Basically, you need something that will let you open YAML files in 
Python with yaml.load). It also adds the *Sonar* directory to the PYTHONPATH 
environment variable so the Python scripts can be run from anywhere.

## Caveats

There are a number of things on the todo list to implement such as code
cleanup, new functionality, and improving comments. Testing has also not been
rigorous so there may (read: probably) be corner cases which are not being
correctly handled and will be fixed when observed. Error handling is fairly 
poor at the moment in areas.

Poor coding choices may also be prevalent. Feel free to suggest alternative
approaches. I may not have done it that way because of legacy reasons or 
because I didn't think about it.

## Contributing

Users are welcomed to make their own branches to experiment. I encourage pull 
requests to improve functionality, error handling, and style. If you find a bug,
please raise an issue and make the problem and reproduction steps/code clear.