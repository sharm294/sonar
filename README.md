# sonar

*sonar* is an automated simulation and testbenching infrastructure for
hardware. The only user input required is a configuration file which defines the 
ports of the device-under-test (DUT), test vectors, and optionally, a set of wait 
conditions. With the configuration file, *sonar* will generate a *.sv* testbench 
and an associated *.dat* file containing the user specified test vectors. It can 
also optionally generate a C++ data file and testbench though that is not quite 
as sophisticated. Some prelimanary work has gone into an object-oriented python 
script approach to generating a configuration file (seen in ``jsonGen/``).

All generated files are placed in a newly created ``./build/`` directory relative
to the path of the configuration file. To simulate the SV file, add the TB, the 
*.dat* file and the the DUT file(s) to the simulator of your choice. To simulate 
the C++ file, make a testbench executable using the generated TB file and run 
it.

## Dependencies

Vivado and Vivado HLS are assumed to be on the PATH. The scripts have been
tested on Bash, with Python 2.7 and Vivado 2017.2 on Ubuntu 16.04. Two
environment variables are also added: SONAR_VIVADO_HLS and SONAR_PATH. It also 
adds the *sonar* directory to the PYTHONPATH environment variable so the Python 
scripts can be run from anywhere. These variables are added to the .bashrc for 
the current user. The package *python-yaml* is required if you want to use a 
YAML-based configuration file (it may be called something different on your 
distro. You need something that will let you open YAML files in Python with 
*yaml.load*). 

## Usage
``source init.sh`` with the correct arguments (run without arguments for help)
to initialize repository first. Provide the absolute path to the cloned 
repository and, optionally, the path to the Vivado HLS include folder for HLS 
header files (usually ``Xilinx/Vivado_HLS/<year>/include``). Remove any trailing 
slashes from the path(s). Then use the make commands to create the sample. 
Running *sonar* on your own designs is easy to do since the Makefile shows the 
command syntax you need.

To create the sample project, run ``make sample``. This will call a number of
targets that create a Vivado HLS project, generate all the testbenches and data 
files and open Vivado for simulation.

If running manually, the top-level script to run is ``sonar.py``. It takes a few
arguments which can be seen by calling ``python sonar.py --help``.

To remove *sonar*, run ``make purge``. The repository can then be deleted, 
leaving no trace of *sonar*

## Folder Hierarchy
*sonar* is designed with the goal that the user can provide overriding functions 
and definitions without editing the core repository. This makes it easy to pull 
new changes because no user code is ever included in git commits.

### include
This folder contains a set of shared functions (``utilities.py``) and definitions
for expanding special strings into numbers (``strToInt.py``). The latter will 
also search the ``user/`` directory for definitions. This folder also contains 
the interface definitions that *sonar* supports (currently AXI-Stream and AXI-
Lite 4) and any associated files. Other interfaces can also be added in ``user/``.

### jsonGen
This folder contains the preliminary work to use an object oriented Python 
script to create a configuration file, rather than writing one out manually. 
It's currently under development. Some exciting things available that *sonar* 
enables is the ability to stream a binary file over AXI-Stream to your TB.

### sample
This is an example project for *sonar*. There are two configuration files
included: a YAML and JSON. Both contain the same information though only the 
YAML has comments as JSON doesn't support comments. Refer to the YAML for more
information about the different keys and dicts. The other files included in 
``sample/`` are:  
* ``sample.cpp``: HLS DUT code
* ``sample.hpp`` and ``utilities.hpp``: headers for ``sample.cpp``
* ``sample.sh``: creates the HLS project by calling ``sample.tcl``
* ``sample_hls.tcl``: creates an HLS project for ``sample.cpp``
* ``sample_vivado.tcl``: creates a Vivado project for simulating the generated
testbench

### src
The core *sonar* modules are here. ``sonar.py`` is the top level file which 
calls the other scripts.

### templates
A template file is included here for each language that *sonar* supports in 
testbench generation.

### user
All the contents of this directory (with the exception of ``__init__.py``) are
excluded from Git. This is intended to support custom user extension to *sonar*
without requiring modifications elsewhere. For example, ``strToInt.py`` will 
look for a file called ``user_strToInt.py`` in this directory and a function in
it called ``strToInt()`` for custom headers. Similarly, user-specific interfaces 
can be added to ``user/interfaces/``. Essentially, ``user/`` functions as a user-
defined version of ``include/``

## Caveats

There are a number of things on the todo list to implement such as code
cleanup, new functionality, and improving comments. Testing has also not been
rigorous so there are probably corner cases that are not being correctly handled 
and will be fixed when observed. Error handling is fairly poor in general at the 
moment. Poor coding choices may also be present. Feel free to suggest alternative
approaches.

## Contributing

I encourage pull requests to improve functionality, error handling, and style. 
If you find a bug, please raise an issue and make the problem and reproduction 
steps/code clear. I also plan to move some of this content to the wiki in the 
future.