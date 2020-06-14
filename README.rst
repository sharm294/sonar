sonar
=====

|Build Status| |codecov| |Quality Gate Status| |Docs|

*sonar* is a simulation/testbenching and project management
infrastructure for Vivado projects.

Testbenching
------------

*sonar* can be imported into a Python script. Then, the user can define
the ports of the device-under-test (DUT) and test vectors. It will
generate a *.sv* testbench and an associated *.dat* file containing the
user specified test vectors. [STRIKEOUT:It can also optionally generate
a C++ data file and testbench for use with HLS though that is not quite
as sophisticated.]\ (this is slated for deprecation or substantial
reworking.)

All generated files are placed in the specified directory. To simulate
the SV file, add the TB, the *.dat* file and the DUT file(s) to the
simulator of your choice. [STRIKEOUT:To simulate the C++ file, make a
testbench executable using the generated TB file and run it.]

*sonar*'s project management and associated scripts show an example
workflow where all these files are automatically added to the created
Vivado projects.

Project Management
------------------

At present, *sonar* can create directories for repositories, and within
these directories, create IPs through its command line interface. For
IPs, a skeleton directory structure is created for the user to fill in
as needed. It provides a set of scripts and a Makefile to compile HLS
IPs, create *sonar* testbenches, and pull them all into Vivado projects.
The goal with management is to provide a consistent feel to hardware
projects, making them easier to navigate, build and share with others.
The reach goal is to add hardware IP dependency information so *sonar*
can go fetch dependencies from other repositories without duplicating
code.

For now, this is experimental.

Usage
-----

To install, clone this repository, go to the cloned directory and run:

.. code:: bash

   $ pip install .

   # start a new shell or login again

   # initialize with local Xilinx path
   $ sonar init vivado /path/to/Xilinx/directory
   # then use "sonar activate vivado_{version}" to change versions
   $ sonar activate vivado_2017.2
   # for now, this should print "sourced file" if successful

The best example for usage can be found in ``tests/shell/sample``. This
example shows a sample C++ source code and an associated testbench
(``sample_src.py``). This testbench file shows the syntax and some of
the features that the *sonar* testbenches can have.

.. code:: python

   # to use the testbench, import sonar in python e.g.
   from sonar.testbench import Testbench, Module, TestVector, Thread
   from sonar.interfaces import AXIS, SAXILite

The ``test.sh`` script in the same directory is part of the *sonar*'s
internal testing. It shows an example of *sonar*'s command line
interface and the commands used to create a new repository, add an IP to
it and simulate it.

.. code:: bash

   # create a repo named 'sample_repo' in the current directory
   $ sonar create repo sample_repo
   $ cd sample_repo || return

   # activate vivado 2017.2, use this repo,
   # set the board to an Alpha Data 8k5
   $ sonar activate vivado_2017.2
   $ sonar repo activate sample_repo
   $ sonar board activate ad_8k5

   # create an IP in this directory named 'sample_ip'
   $ sonar create ip sample_ip

   # add source files and add the name of the file to the Makefile

   # generate the HLS IP
   $ make hw-sample_src

   # generate the sonar TB
   $ make config-sample_src

   # create a vivado project for sample_src and simulate it in terminal
   $ ./run.sh cad sample_src batch behav 1 0 0 0 0

Dependencies
------------

Testbench
~~~~~~~~~

Installing the package is sufficient. It is recommended to install and
setup `argcompete`_ to autocomplete *sonar*'s CLI commands. If the
package exists, *sonar* will use it.

Pytest
~~~~~~

`pytest`_ and coverage is used for internal testing.

Development
~~~~~~~~~~~

For development, it is HIGHLY recommended to use a virtual env such as
`conda`_ or docker. *sonar* uses the `pre-commit`_ package to enforce
style checks for every commit. There are a number of additional packages
needed for all the pre-commit hooks to run, including clang-format,
cppcheck, cpplint, shellcheck, and gitlint among others. If you're using
conda, most can be installed from conda-forge or pip but some may need
custom download channels.

.. |Build Status| image:: https://travis-ci.org/sharm294/sonar.svg?branch=master
   :target: https://travis-ci.org/sharm294/sonar
.. |codecov| image:: https://codecov.io/gh/sharm294/sonar/branch/dev/graph/badge.svg
   :target: https://codecov.io/gh/sharm294/sonar
.. |Quality Gate Status| image:: https://sonarcloud.io/api/project_badges/measure?project=sharm294_sonar&metric=alert_status
   :target: https://sonarcloud.io/dashboard?id=sharm294_sonar
.. |Docs| image:: https://readthedocs.org/projects/sonar/badge/?version=latest
   :target: https://sonar.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. _argcompete: https://github.com/kislyuk/argcomplete#global-completion
.. _pytest: https://docs.pytest.org/en/stable/
.. _conda: https://docs.conda.io/en/latest/miniconda.html
.. _pre-commit: https://pre-commit.com/
