import sys
import math
import inspect

class ap_fifo(object):
    
    def __init__(self, parameters):

        if not('name' in parameters):
            raise ValueError('Name must exist')
        else:
            self.name = parameters['name']

        if not('direction' in parameters):
            raise ValueError('Direction must exist')
        else:
            self.direction = parameters['direction']

        #define a default ap_fifo channel
        if not('channels' in parameters):
            parameters.update({"channels": [
                                            {'name':'data', 'type':'tdata', 'size': 8},
                                            {'name':'valid', 'type':'tvalid'},
                                            {'name':'ready', 'type':'tready'},
                                            ]
                                })
        
        self.parameters = parameters
                                            
        for dictItem in self.parameters['channels']:
            if dictItem['type'] == 'rd_data' or dictItem['type'] == 'wr_data':
                if 'size' in dictItem:
                    size = int(dictItem['size'])
                else:
                    size = 8


        self.streamLen = ((size - 1) / 8) + 1



    def streamTransaction(self, payload):
        fifo_name = self.parameters['name']
        dictElement = {"interface" : {"type": "ap_fifo", "name": fifo_name, "payload" : [payload]}}
        return dictElement


    def rd_enFunction(self, binArray, transIndex, endian):
        return 1
    
    def rd_dataFunction(self, binArray, transIndex, endian):
        tdata_bytes = [binArray[i] for i in range(transIndex, transIndex + self.streamLen) if (i < len(binArray))]
        tdata_bytes += [0]*(self.streamLen-len(tdata_bytes)) ## Pad the byte list if the last word isn't "filled" all the way

        if endian == 'little':
            tdata_bytes.reverse()

        tdata = reduce((lambda x, y: (x << 8) | y), tdata_bytes)
        return tdata
    
    def empty_nFunction(self, binArray, transIndex, endian):
        return 1
    
    def wr_enFunction(self, binArray, transIndex, endian):
        return 1
    
    def wr_dataFunction(self, binArray, transIndex, endian):
        tdata_bytes = [binArray[i] for i in range(transIndex, transIndex + self.streamLen) if (i < len(binArray))]
        tdata_bytes += [0]*(self.streamLen-len(tdata_bytes)) ## Pad the byte list if the last word isn't "filled" all the way

        if endian == 'little':
            tdata_bytes.reverse()

        tdata = reduce((lambda x, y: (x << 8) | y), tdata_bytes)
        return tdata
    
    def full_nFunction(self, binArray, transIndex, endian):
        return 1
    


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
        fifo_name = self.parameters['name']

        # direction = self.parameters['direction']
        # if (direction == 'read'): 
        #     self.parameters['wr_en'] = 
        # elif(direction == 'write'):
        #     self.parameters['rd_en'] = 


        bin_array_len = len(binArray)
        while transIndex < (math.ceil(bin_array_len/float(self.streamLen)) * self.streamLen):
            
            tdata_bytes = [binArray[i] for i in range(transIndex, transIndex + self.streamLen) if (i < len(binArray))]
            tdata_bytes += [0]*(self.streamLen-len(tdata_bytes)) ## Pad the byte list if the last word isn't "filled" all the way

            if endian == 'little':
                tdata_bytes.reverse()

            tdata = reduce((lambda x, y: (x << 8) | y), tdata_bytes)

            payload = {"tdata": "0x" + format(tdata, '08x')}
            for item in self.parameters['channels']:
                #print item
                if functionsDict != None and  item['type'] in functionsDict:
                    val = functionsDict[item['type']](binArray, transIndex, endian)
                elif item['type'] != 'tdata' and item['type'] != 'tvalid' and item['type'] != 'tready':
                    if (hasattr(self, item['type'] + "Function")):
                        func=getattr(self, item['type'] + "Function")
                        val=func(binArray, transIndex, endian)
                        payload.update({item['type'] : val})

            
            retList.append(self.streamTransaction(payload)) 
            transIndex = transIndex + self.streamLen
            
        
        
        return retList





#test for this module
if __name__=="__main__":
    
    
    #writing random garbage data to test.txt
    with open("test_ap_fifo.bin", "wb") as binary_file:
        num_bytes_written = binary_file.write(b'\xDE\xAD\xBE\xEF\xFA\xCE\xFA\xCE')
        num_bytes_written = binary_file.write(b'\x11\x22\x33\x44\x55\x66\x77\x88')
        num_bytes_written = binary_file.write(b'\x00\xaa\xbb\xcc\xdd\xee\xff\x12')
        num_bytes_written = binary_file.write(b'\x34\x56\x78')
    
    

    #reading back random garbage data from test.txt
    with open("test_ap_fifo.bin", "rb") as binary_file:
        data = binary_file.read()
   
    #now have data in byte array
    dataArray = bytearray()
    dataArray.extend(data)
    



    ap_fifo_in = ap_fifo({"name":"ap_fifo_in", "direction":"read", "channels": [
                                                        {"name":"data", "type": "tdata", "size": 64},
                                                        {"name":"keep", "type": "tkeep"},
                                                        {"name":"valid", "type": "tvalid"},
                                                        {"name":"ready", "type": "tready"},
                                                        {"name":"last", "type": "tlast"},
                                                        ]
                                                                            
                })
    retList = ap_fifo_in.binToStream(dataArray, None)

    print "Printing the Dict for binary transaction"
    for item in retList:
        print item
