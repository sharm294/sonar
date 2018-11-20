import sys
import math
import inspect

class axis(object):
    
    def __init__(self, parameters):

        if not('name' in parameters):
            raise ValueError('Name must exist')
        else:
            self.name = parameters['name']

        if not('direction' in parameters):
            raise ValueError('Direction must exist')
        else:
            self.direction = parameters['direction']

        #define a default axistream channel
        if not('channels' in parameters):
            parameters.update({"channels": [
                                            {'name':'data', 'type':'tdata', 'size': 8},
                                            {'name':'valid', 'type':'tvalid'},
                                            {'name':'ready', 'type':'tready'},
                                            ]
                                })
        
        self.parameters = parameters
                                            
        for dictItem in self.parameters['channels']:
            if dictItem['type'] == 'tdata':
                if 'size' in dictItem:
                    size = dictItem['size']
                else:
                    size = 8


        self.streamLen = size / 8



    def streamTransaction(self, payload):
        axisName = self.parameters['name']
        dictElement = {"interface" : {"type": "axis", "name": axisName, "payload" : [payload]}}
        return dictElement


    def tkeepFunction(self, binArray, transIndex, endian):

        if transIndex < ((math.ceil(len(binArray)/8.0) - 1) * 8.0) :
            tkeep = "KEEP_ALL"
        else:
            sizeofLastTransaction = len(binArray) % self.streamLen 
            if sizeofLastTransaction != self.streamLen:
                tkeep = ''
                for i in range(0, self.streamLen - sizeofLastTransaction):
                    if endian == 'big':
                        tkeep = "0" + tkeep 
                    else: #little endian
                        tkeep = tkeep + "0" 

                for i in range(self.streamLen - sizeofLastTransaction, self.streamLen):
                    if endian == 'big':
                        tkeep = "1" + tkeep 
                    else: #little endian
                        tkeep = tkeep + "1" 
                
                tkeep = "0b" + tkeep

            else:
                tkeep = "KEEP_ALL"


        return tkeep

    def tlastFunction(self, binArray, transIndex, endian):

        if transIndex < ((math.ceil(len(binArray)/8.0) - 1) * 8) :
            tlast = 0
        else:
            tlast = 1
        
        return tlast


    def binToStream(self, binArray, functionsDict, endian='little'):
        retList = []
        transIndex = 0
        axisName = self.parameters['name']


        while transIndex < ((math.ceil(len(binArray)/8.0)) * 8):
            
            tdata = 0
            for i in range(transIndex, transIndex + self.streamLen ):
                if endian == 'little':
                    if i < len(binArray):
                        tdata = (tdata >> 8) | ( binArray [i] << 56) 
                    elif i < transIndex + self.streamLen:
                        tdata = tdata >> 8
                else: #big endian
                    if i < len(binArray):
                        tdata = (tdata << 8) | ( binArray [i]) 
                    elif i < transIndex + self.streamLen:
                        tdata = tdata << 8


            payload = {"tdata": "0x" + format(tdata, '08x')}
            for item in self.parameters['channels']:
                #print item
                if functionsDict != None and  item['type'] in functionsDict:
                    val = functionsDict[item['type']](binArray, transIndex, endian)
                elif item['type'] != 'tdata' and item['type'] != 'tvalid' and item['type'] != 'tready':
                    func=getattr(self, item['type'] + "Function")
                    val=func(binArray, transIndex, endian)
                    payload.update({item['type'] : val})

            
            retList.append(self.streamTransaction(payload)) 
            transIndex = transIndex + self.streamLen
            
        
        
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
    



    axisIn = axis({"name":"axisIn", "direction":"slave", "channels": [
                                                        {"name":"data", "type": "tdata", "size": 64},
                                                        {"name":"keep", "type": "tkeep"},
                                                        {"name":"valid", "type": "tvalid"},
                                                        {"name":"ready", "type": "tready"},
                                                        {"name":"last", "type": "tlast"},
                                                        ]
                                                                            
                })
    retList = axisIn.binToStream(dataArray, None)

    print "Printing the Dict for binary transaction"
    for item in retList:
        print item
