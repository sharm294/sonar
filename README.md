# sonar

*sonar* is a simulation and testbenching infrastructure for hardware. It can 
be imported into a Python script as a library. Then, the user can define the 
ports of the device-under-test (DUT) and test vectors. *sonar* will generate 
a *.sv* testbench and an associated *.dat* file containing the user specified 
test vectors. It can also optionally generate a C++ data file and testbench for 
use with HLS though that is not quite as sophisticated.

All generated files are placed in the specified directory. To simulate the 
SV file, add the TB, the *.dat* file and the the DUT file(s) to the simulator 
of your choice. To simulate the C++ file, make a testbench executable using the 
generated TB file and run it.

## Dependencies

Vivado and (and optionally) Vivado HLS are assumed to be on the PATH. The 
Makefile will complain if that's not the case. Bash, gcc and make are also 
needed.  The scripts have been tested with Bash 4.3.48, gcc 5.4.0 and make 4.1 
(though any sufficiently modern version of these three should work) and with 
Python 2.7 (Python 3 isn't supported yet) and Vivado 2017.2 on Ubuntu 16.04. Some
TCL files assert Vivado version checks. As people use different versions and any 
version differences are identified, code for handling those versions will be 
added. Two environment variables are also added: SONAR_VIVADO_HLS and SONAR_PATH. 
It also adds the *sonar* directory to the PYTHONPATH environment variable so the 
Python scripts can be run from anywhere. These variables are added to the .bashrc 
for the current user.).

## Usage
``source init.sh`` and follow the directions.

To create the sample project, run ``make``. This will call a number of
targets that create a Vivado HLS project (if the SONAR_VIVADO_HLS variable is 
set from ``init.sh``), generate all the testbenches and data files and open 
Vivado for simulation.

*sonar* can be imported into any Python script. Refer to /sample/sample.py or 
in /sonar/tests/ for examples.

To remove *sonar*, ``source purge.sh``. The repository can then be deleted, 
leaving no trace of *sonar*

## Folder Hierarchy

### sonar

#### core
The core *sonar* modules are here. ``sonar.py`` is the top level file which 
calls the other scripts. The backend is in need of documentation and cleanup.

##### include
This folder contains a set of shared functions (``utilities.py``) and definitions
for expanding special strings into numbers (``strToInt.py``). The latter will 
also search the ``user/`` directory for definitions. This folder also contains 
the interface definitions that *sonar* supports (currently AXI-Stream and AXI-
Lite 4) and any associated files. Other interfaces can also be added in ``user/``.

##### templates
A template file is included here for each language that *sonar* supports in 
testbench generation.

#### test
Example or test scripts for internal *sonar* functions will be here.

### sample
This is an example project for *sonar*. The files included in ``sample/`` are:  
* ``sample.cpp``: HLS DUT code
* ``sample.hpp`` and ``utilities.hpp``: headers for ``sample.cpp``
* ``sample.sh``: creates the HLS project by calling ``sample.tcl``
* ``sample_hls.tcl``: creates an HLS project for ``sample.cpp``
* ``sample_vivado.tcl``: creates a Vivado project for simulating the generated
* ``sample.py``: example Python script called from ``make`` that creates a 
testbench
* ``sample.v``: Verilog code from HLS if HLS isn't used or available

## Caveats

There are a number of things on the todo list to implement such as code
cleanup, new functionality, and improving comments. Testing has also not been
rigorous so there are probably corner cases that are not being correctly handled 
and will be fixed when observed. Error handling is fairly poor in general at the 
moment. Poor coding choices may also be present.

## Contributing

I encourage forks/PRs to improve functionality, error handling, and style. 
If you find a bug, please raise an issue and make the problem and reproduction 
steps/code clear. For style, I've tried to adhere to good Python style and 
Google-style docstrings on the more public code (the core is not compliant at 
all). I'm also using a ~60 char width limit on future commit messages.
