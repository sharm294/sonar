# sonar

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=sharm294_sonar&metric=alert_status)](https://sonarcloud.io/dashboard?id=sharm294_sonar)
[![Build Status](https://travis-ci.org/sharm294/sonar.svg?branch=dev)](https://travis-ci.org/sharm294/sonar)
[![codecov](https://codecov.io/gh/sharm294/sonar/branch/master/graph/badge.svg)](https://codecov.io/gh/sharm294/sonar)


*sonar* is a project management and simulation/testbenching infrastructure for hardware.

#### Project Management

At present, *sonar* can create directories for repositories, and within these directories, create IPs through its command line interface.
For IPs, a skeleton directory structure is created for the user to fill in as needed.
It provides a set of scripts and a Makefile to compile HLS IPs, create *sonar* testbenches, and pull them all into Vivado projects.

#### Testbenching

It can be imported into a Python script.
Then, the user can define the ports of the device-under-test (DUT) and test vectors.
*sonar* will generate a *.sv* testbench and an associated *.dat* file containing the user specified test vectors. ~~It can also optionally generate a C++ data file and testbench for use with HLS though that is not quite as sophisticated.~~
(this is slated for deprecation or substantial reworking.)

All generated files are placed in the specified directory.
To simulate the SV file, add the TB, the *.dat* file and the DUT file(s) to the simulator of your choice.
~~To simulate the C++ file, make a testbench executable using the generated TB file and run it.~~

*sonar*'s project management and associated scripts show an example workflow where all these files are automatically added to the created Vivado projects.

## Usage

To install, clone this repository, go to the cloned directory and run:
```bash
$ pip install .

# initialize with local Xilinx path
$ sonar init vivado /path/to/Xilinx/directory
# then use "sonar activate vivado_{version}" to change versions
$ sonar activate vivado_2017.2
```

The best example for usage can be found in `tests/shell/sample`.
This example shows a sample C++ source code and an associated testbench (`sample_src.py`).
This testbench file shows the syntax and some of the features that the *sonar* testbenches can have.

```python
# to use the testbench, import sonar in python e.g.
from sonar.testbench import Testbench, Module, TestVector, Thread
from sonar.interfaces import AXIS, SAXILite
```

The `test.sh` script in the same directory is part of the *sonar*'s internal testing.
It shows an example of *sonar*'s command line interface and the commands used to create a new repository, add an IP to it and simulate it.

```bash
$ sonar create repo sample_repo
$ cd sample_repo
$ sonar activate vivado_2017.2
$ sonar repo activate sample_repo
$ sonar board activate ad_8k5
$ sonar create ip sample_ip
```

## Dependencies

These are the current dependencies of *sonar*. Note, this may become outdated.

### Testbench

Installing the package is sufficient.
Its dependencies are the argcomplete and toml packages which are installed automatically.
It is recommended to setup [argcompete](https://github.com/kislyuk/argcomplete#global-completion) to autocomplete *sonar* CLI options.

### Pytest

[pytest](https://docs.pytest.org/en/stable/) is used for internal testing.

### Development

For development, it is HIGHLY recommended to use a virtual env such as [conda](https://docs.conda.io/en/latest/miniconda.html) or docker.
*sonar* uses the [pre-commit](https://pre-commit.com/) package to enforce style checks for every commit.
There are a number of additional packages needed for all the pre-commit hooks to run.
