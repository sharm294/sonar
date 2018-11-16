from axis import axis
from parallelSection import ParallelSection


class TestVector(object):
    def __init__(self):
        self.sections = []

    def addSection(self, section):
        self.sections.append(section)

    def getDict(self):
        retList = []
        for idx,section in enumerate(self.sections):
            retList.append({"Parallel_Section_" + str(idx) : section.getDict()})
        
        return retList

    def getWaits(self):

        waitList = []
        for section in self.sections:
            for key in section.waitConditions.keys():
                waitList.append({"condition": section.waitConditions[key], "key" : key})

        return waitList


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

    print "Adding Sec to Test Vector"

    testVector0 = TestVector()
    testVector0.addSection(sec)
    testVector0.addSection(sec)
    print testVector0.getDict()
    print testVector0.getWaits()


