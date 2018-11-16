from axis import axis


class ParallelSection(object):
    def __init__(self):
        self.dict = []
        self.waitConditions = {}

    def addWait(self, key, condition):
        self.dict.append({"wait": {"key" : key}})
        self.waitConditions.update({key : condition})

    def addMacro(self, macro):
        self.dict.append({"macro": macro})

    def addSignal(self, parameters):
        self.dict.append({"signal": parameters})

    def addDelay(self, delay):
        self.dict.append({"delay" : delay})

    def addBurst(self, burst):
        for transaction in burst:
            self.dict.append(transaction)


    def printDict(self):
        print self.dict

    def getDict(self):
        return self.dict

#test for this module
if __name__=="__main__":


    #writing random garbage data to test.txt
    with open("test_sec.bin", "wb") as binary_file:
        num_bytes_written = binary_file.write(b'\xDE\xAD\xBE\xEF\xFA\xCE\xFA\xCE')
        num_bytes_written = binary_file.write(b'\x11\x22\x33\x44\x55\x66\x77\x88')
        num_bytes_written = binary_file.write(b'\x00\xaa\xbb\xcc\xdd\xee\xff\x12')
        num_bytes_written = binary_file.write(b'\x34\x56\x78')
    
    

    #reading back random garbage data from test.txt
    with open("test_sec.bin", "rb") as binary_file:
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

    sec = ParallelSection()


    sec.addWait("mem_ready", "wait(mem_ready);")
    sec.addMacro("INIT_SIGNALS")
    sec.addDelay("40ns")
    sec.addBurst(retList)
    sec.printDict()
