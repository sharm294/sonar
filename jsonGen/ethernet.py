import sys
import math
import inspect
from axis import axis


#packet types

class Ethernet(axis):
    
    def __init__(self, parameters):
        axis.__init__(self, parameters)


        if 'mac_addr_dst' in parameters:
            self.mac_addr_dst = parameters['mac_addr_dst']
        else:
            self.mac_addr_dst = '0xFFFFFFFFFFFF' 

        if 'mac_addr_src' in parameters:
            self.mac_addr_src = parameters['mac_addr_src']
        else:
            self.mac_addr_src = '0xFFFFFFFFFFFF' 

        if 'ether_type' in parameters:
            self.ether_type = parameters['ether_type']
        else:
            self.ether_type = '0x7400'

        if 'prefix' in parameters:
            self.prefix = parameters['prefix']
        else:
            self.prefix = None
        
        if 'suffix' in parameters:
            self.suffix = parameters['suffix']
        else:
            self.suffix = None



    def setMACDst(self, mac_addr_dst):
        self.mac_addr_dst = mac_addr_dst
    
    def setMACSrc(self, mac_addr_src):
        self.mac_addr_src = mac_addr_src
    
    def setEtherType(self, ether_type):
        self.ether_type = ether_type
    
    def setPrefix(self, prefix):
        self.prefix = prefix
    
    def setSuffix(self, suffix):
        self.suffix = suffix


    def binToStream(self, binArray, functionsDict):
        waitlist = None


        if not(self.prefix == None):
            binArray[0:0] = bytearray.fromhex(self.prefix[2:])

        binArray[0:0] = bytearray.fromhex(self.ether_type[2:])
        binArray[0:0] = bytearray.fromhex(self.mac_addr_src[2:])
        binArray[0:0] = bytearray.fromhex(self.mac_addr_dst[2:])
        
        if not(self.suffix == None):
            binArray.extend(bytearray.fromhex(self.suffix[2:]))
        
        retList = axis.binToStream(self, binArray, functionsDict)
        
        
        return retList


    def getHeader(self):


        binArray = bytearray.fromhex(self.mac_addr_dst[2:])
        binArray.extend(bytearray.fromhex(self.mac_addr_src[2:]))
        binArray.extend(bytearray.fromhex(self.ether_type[2:]))
        
        if not(self.prefix == None):
            binArray.extend(bytearray.fromhex(self.prefix[2:]))

        return binArray 



    def waitForHeader(self, key):
        retList = []

        for dictItem in self.parameters['channels']:
            if dictItem['type'] == 'tdata':
                axisName = dictItem['name']
                break


        
        retList.append({"key": key + "_0", "condition": "wait(" + self.name + "_" + axisName + "[63:56]==8'h" + self.mac_addr_src[2:3]
            + " && " + self.name + "_" + axisName + "[55:48]==8'h" + self.mac_addr_src[3:4] 
            + " && " + self.name + "_" + axisName + "[47:40]==8'h" + self.mac_addr_dst[12:13] 
            + " && " + self.name + "_" + axisName + "[39:32]==8'h" + self.mac_addr_dst[10:11] 
            + " && " + self.name + "_" + axisName + "[32:23]==8'h" + self.mac_addr_dst[8:9] 
            + " && " + self.name + "_" + axisName + "[23:16]==8'h" + self.mac_addr_dst[6:7] 
            + " && " + self.name + "_" + axisName + "[15:8]==8'h" + self.mac_addr_dst[4:5] 
            + " && " + self.name + "_" + axisName + "[7:0]==8'h" + self.mac_addr_dst[2:3] 
            + ");"
            
            })
        
        retList.append({"key": key + "_1", "condition": "wait(" 
            + " && " + self.name + "_" + axisName + "[47:40]==8'h" + self.ether_type[4:5] 
            + " && " + self.name + "_" + axisName + "[39:32]==8'h" + self.ether_type[2:3] 
            + " && " + self.name + "_" + axisName + "[32:23]==8'h" + self.mac_addr_src[12:13] 
            + " && " + self.name + "_" + axisName + "[23:16]==8'h" + self.mac_addr_src[10:11] 
            + " && " + self.name + "_" + axisName + "[15:8]==8'h" + self.mac_addr_src[8:9] 
            + " && " + self.name + "_" + axisName + "[7:0]==8'h" + self.mac_addr_src[6:7] 
            + ");"
            })
       

        return retList



#test for this module
if __name__=="__main__":
    
    
    #writing random garbage data to test.txt
    with open("test_axis.bin", "wb") as binary_file:
        num_bytes_written = binary_file.write(b'\xDE\xAD\xBE\xEF\xFA\xCE\xFA\xCE')
        num_bytes_written = binary_file.write(b'\x11\x22\x33\x44\x55\x66\x77\x88')
        num_bytes_written = binary_file.write(b'\x00\xaa\xbb\xcc\xdd\xee\xff\x12')
        num_bytes_written = binary_file.write(b'\x34\x56\x78')
    
    

    #reading back random garbage data from test.txt
    with open("test_axis.bin", "rb") as binary_file:
        data = binary_file.read()
   
    #now have data in byte array
    dataArray = bytearray()
    dataArray.extend(data)
    



    ethernetPort = Ethernet({"name":"axisIn", "mac_addr_dst": "0x112233445566", "mac_addr_src":"0xaabbccddeeff", "direction":"slave", "channels": [
                                                        {"name":"data", "type": "tdata", "size": 64},
                                                        {"name":"keep", "type": "tkeep"},
                                                        {"name":"valid", "type": "tvalid"},
                                                        {"name":"ready", "type": "tready"},
                                                        {"name":"last", "type": "tlast"},
                                                        ]
                                                                            
                })
    ethernetPort.setPrefix('0x0011')
    retList = ethernetPort.binToStream(dataArray, None)
    retList.append(ethernetPort.waitForHeader("test"))
    
    print "Printing the Dict for binary transaction and wait"
    for item in retList:
        print item
