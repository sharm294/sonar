********
Projects
********

Purpose
=======

These testbenches are included as examples in conjunction with IP source files.
Together, these files can be used to run the testbench to validate the IPs, which
is done as part of the testing for sonar.

Running these testbenches can be accomplished in one of two ways.

One method is to call the testbench-generating Python script, and then run the
testbench in an appropriate simulation tool (e.g. compiling the executable for
C++ or adding all source files to XSIM). This is the manual approach.

The second method is to emulate the method used in the tests for sonar. Refer to
the tests/shell/* for scripts on how to do this. A test.sh script is included
for each testbench project that contains the command-line commands to set up
a repository, add an IP and run the testbench. This is a more automated approach.

Testbenches
===========

The testbenches included here are described below.

.. include:: ./hello_world/README.rst
