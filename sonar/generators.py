from math import ceil

from .base_types import SonarObject
from .interfaces import AXIS

class EthernetAXIS(AXIS):
    
    def __init__(self, name, direction, clock, mac_src, mac_dst, ether_type, 
            prefix=None, suffix=None, c_struct=None, c_stream=None):
        AXIS.__init__(self, name, direction, clock, c_struct, c_stream)
        self.mac_src = mac_src
        self.mac_dst = mac_dst
        self.ether_type = ether_type
        self.prefix = prefix
        self.suffix = suffix

        self.header = self.mac_dst[2:] + self.mac_src[2:] + self.ether_type[2:]

    def file_to_stream(self, thread, filePath, parsingFunc=None, endian='little'):
        transactions = {}
        if parsingFunc is None:
            parsingFunc = self._f2sBinData
        if filePath.endswith('.bin'):
            with open(filePath) as f:
                readData = f.read()
                binData = bytearray(readData)
                if self.prefix is not None:
                    binData[0:0] = bytearray.fromhex(self.prefix[2:])

                binData[0:0] = bytearray.fromhex(self.header)
                
                if self.suffix is not None:
                    binData.extend(bytearray.fromhex(self.suffix[2:]))
                self._file_to_stream(thread, binData, parsingFunc, endian)
        else:
            raise NotImplementedError()

    def raw_file_to_stream(self, thread, filePath, parsingFunc=None, endian='little'):
        AXIS.file_to_stream(thread, filePath, parsingFunc, endian)

    def get_header_bytes(self):
        binArray = bytearray.fromhex(header)
        
        if self.prefix is not None:
            binArray.extend(bytearray.fromhex(self.prefix[2:]))

        return binArray

    def wait_for_header(self, thread, endian='little'):
        octet = [0] * 14
        octet[0] = self.mac_dst[2:4]
        octet[1] = self.mac_dst[4:6]
        octet[2] = self.mac_dst[6:8]
        octet[3] = self.mac_dst[8:10]
        octet[4] = self.mac_dst[10:12]
        octet[5] = self.mac_dst[12:14]
        octet[6] = self.mac_src[2:4]
        octet[7] = self.mac_src[4:6]
        octet[8] = self.mac_src[6:8]
        octet[9] = self.mac_src[8:10]
        octet[10] = self.mac_src[10:12]
        octet[11] = self.mac_src[12:14]
        octet[12] = self.ether_type[2:4]
        octet[13] = self.ether_type[4:6]

        data_width = self.port.get_channel('tdata')['size']/8
        wait_str = ""
        word_count = 0

        while (word_count < ceil(14.0/data_width)):
            octet_count = word_count*data_width
            min_value = min(data_width, 14-octet_count)
            word = "0x"
            if endian == 'little':
                for i in range(min_value):
                    upper_index = (((min_value-i)) * 8) - 1
                    lower_index = (min_value-i-1)*8
                    octet_index = octet_count + min_value - i - 1
                    word += octet[octet_index]
                wait_str += (self.name + "_tdata[" + str(min_value*8-1) + ":0] == $value")
            else:
                for i in range(min_value):
                    upper_index = ((i+1) * 8) - 1
                    lower_index = i*8
                    octet_index = octet_count + i
                    word += octet[octet_index]
                wait_str += (self.name + "_tdata[" + str(data_width*8-1) + ":" + str((data_width - min_value)*8) + "] == $value")
            thread.wait_level(wait_str, word)
            wait_str = ""
            word_count += 1