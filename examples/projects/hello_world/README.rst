Hello World
-----------

This project shows an example of most of the core functionality of sonar. The
DUT here is an HLS streaming IP that has:

- an AXI4-Lite slave interface,
- a pair of master/slave AXI4-Stream (AXIS) interfaces
- an output ``ack`` signal

After writing 1 to the ``enable`` register, the IP reads one beat from the input
AXIS interface, absorbs it and sets the ``ack`` signal high. The next beat that is
read from the input AXIS has its ``tdata`` incremented by one and then sent out
over the output AXIS interface.
