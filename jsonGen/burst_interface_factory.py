from axis import axis
from ap_fifo import ap_fifo
from axi4stream import axi4stream

class burst_interface_factory(object):

    @staticmethod
    def build(interface_type, interface_constructor_hash):
        burst_interface = None
        if (interface_type == "axis"):
            burst_interface = axis(interface_constructor_hash)
        elif (interface_type == "axi4stream"):
            burst_interface = axi4stream(interface_constructor_hash)
        elif (interface_type == "ap_fifo"):
            burst_interface = ap_fifo(interface_constructor_hash)
        else:
            print "type " + interface_type + " is currently unsupported in burst_interface_factory"
            exit -1

        return burst_interface