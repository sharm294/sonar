*****
sonar
*****

+---------------+-----------------------+-----------------------+
|    Service    |         Master        | Dev                   |
+===============+=======================+=======================+
| Build         | |Build Status Master| | |Build Status Dev|    |
+---------------+-----------------------+-----------------------+
| Coverage      | |codecov Master|      | |codecov Dev|         |
+---------------+-----------------------+-----------------------+
| Quality       | |Quality Gate Master| | |Quality Gate Dev|    |
+---------------+-----------------------+-----------------------+
| Documentation |                       | |Docs|                |
+---------------+-----------------------+-----------------------+

*sonar* is a simulation/testbenching and project management
infrastructure for Vivado projects.

Testbenching
============

*sonar* can be imported into a Python script. Then, the user can define
the ports of the device-under-test (DUT) and test vectors. It will
generate a *.sv* testbench and an associated *.dat* file containing the
user specified test vectors. It can also optionally generate a C++ data file
and testbench for use with HLS though that is not quite as sophisticated.

All generated files are placed in the specified directory. To simulate
the SV file, add the TB, the *.dat* file and the DUT file(s) to the
simulator of your choice. To simulate the C++ file, make a testbench executable
using the generated TB file and run it.

*sonar*'s project management and associated scripts show an example
workflow where all these files are automatically added to the created
Vivado projects.

Project Management
==================

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
=====

To install, clone this repository, go to the cloned directory and run:

.. code:: bash

  $ pip install .

  # start a new shell or login again

  # initialize with local Xilinx path
  $ sonar init vivado /path/to/Xilinx/directory
  # then use "sonar activate vivado_{version}" to change versions
  $ sonar activate vivado_2017.2
  # for now, this should print "sourced file" if successful

The best example for usage can be found in ``docs/projects/hello_world``. This
example shows a sample C++ source code and an associated testbench
(``hello_world.py``). This testbench file shows the syntax and some of
the features that the *sonar* testbenches can have.

.. code:: python

  # to use the testbench, import sonar in python e.g.
  from sonar.testbench import Testbench, Module, TestVector, Thread

The ``test_hello_world.sh`` script in ``tests/shell`` is part of the *sonar*'s
internal testing. It shows an example of *sonar*'s command line
interface and the commands used to create a new repository, add an IP to
it and simulate it.

Dependencies
============

Testbench
---------

Installing the package is sufficient. It is recommended to install and
setup `argcomplete`_ to autocomplete *sonar*'s CLI commands. If the
package exists, *sonar* will use it.

Pytest
------

`pytest`_ and coverage is used for internal testing.

Development
-----------

For development, it is HIGHLY recommended to use a virtual env such as
`conda`_ or docker. *sonar* uses the `pre-commit`_ package to enforce
style checks for every commit. Conda instructions to set up the development
environment are below:

.. code:: bash

  # install sonar as editable
  $ pip install -e .

  # install optional but RECOMMENDED packages
  conda install argcomplete

  # install testing dependencies
  $ conda install pytest coverage

  # install pre-commit and pre-commit hooks
  $ conda install pylint
  $ conda install -c conda-forge pre-commit cpplint cppcheck shellcheck
  $ conda install -c sarcasm clang-format

  # activate argcomplete globally for your user if it's not otherwise activated
  # note: make sure user bash completion scripts are picked up by .bashrc!
  $ activate-global-python-argcomplete --user

  # install pre-commit if not installed for this repository
  $ pre-commit install

.. |Build Status Master| image:: https://travis-ci.org/sharm294/sonar.svg?branch=master
  :target: https://travis-ci.org/sharm294/sonar
.. |Build Status Dev| image:: https://travis-ci.org/sharm294/sonar.svg?branch=dev
  :target: https://travis-ci.org/sharm294/sonar
.. |codecov Master| image:: https://codecov.io/gh/sharm294/sonar/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/sharm294/sonar
.. |codecov Dev| image:: https://codecov.io/gh/sharm294/sonar/branch/dev/graph/badge.svg
  :target: https://codecov.io/gh/sharm294/sonar
.. |Quality Gate Master| image:: https://sonarcloud.io/api/project_badges/measure?project=sharm294_sonar&metric=alert_status
  :target: https://sonarcloud.io/dashboard?id=sharm294_sonar
.. |Quality Gate Dev| image:: https://sonarcloud.io/api/project_badges/measure?branch=dev&project=sharm294_sonar&metric=alert_status
  :target: https://sonarcloud.io/dashboard?id=sharm294_sonar&branch=dev
.. |Docs| image:: https://readthedocs.org/projects/sonar/badge/?version=latest
  :target: https://sonar.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status
.. _argcomplete: https://github.com/kislyuk/argcomplete#global-completion
.. _pytest: https://docs.pytest.org/en/stable/
.. _conda: https://docs.conda.io/en/latest/miniconda.html
.. _pre-commit: https://pre-commit.com/
