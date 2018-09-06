# shoal-share

This repository contains the shared code for Shoal (working name) - a high level communication  infrastructure for PGAS as part of Galapagos. For portability, some parts of this repository has applications beyond Shoal as described below.

## JSON-Testbench
This provides a JSON-based testbenching infrastructure for CSim and SV. The user can specify data in JSON which can be parsed and eventually read by the testbench. The python scripts used for parsing are in ``testbench/`` and an example is provided in ``testbench/sample/``. The files here are:
* ``sample_tb.cpp``: example C++ testbench for CSim
* ``sample_tb.sv``: example SV testbench. The evaluateData task is important to look at.
* ``sample.cpp``: HLS DUT
* ``sample.hpp``: header for ``sample.cpp``
* ``sample.json``: example user JSON file. Documentation for the JSON file structure is included here
* ``sample.sh``: creates the HLS project by calling ``sample.tcl``
* ``sample.tcl``: creates an HLS project for ``sample.cpp``

A Vivado project for sample can be created by adding the .v file from HLS, the systemverilog testbench, axis_interface.sv and sample_sv.dat to the project. Note that the files must be in the same directory.

## Usage
``source init.sh`` with the correct arguments (run without args for help) to initialize repository. Then use the appropriate make commands or run scripts as needed. ``make sample`` and ``make hw`` are two examples.

## Dependencies

Vivado and Vivado HLS are assumed to be on the PATH. The scripts have been tested on Bash, with Python 2.7 and Vivado 2017.2 on Ubuntu 16.04. Two environment variables are also added: SHOAL_VIVADO_HLS and SHOAL_SHARE_PATH