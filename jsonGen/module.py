from axis import axis
from parallelSection import ParallelSection
from testVector import TestVector
import json



class Module:
    def __init__(self, name):
        self.name = name
        self.ports = []
        self.vecs = []
        self.waitConditions = []
    def addPort(self, port):
        self.ports.append(port)

    def addVec(self, vector):
        self.vecs.append({"Test_Vector_" + str(len(self.vecs)) : vector.getDict()})
        self.waitConditions.extend(vector.getWaits())
    
    def getJSON(self):

        retDict = {"Flag_Count" : 4, 
                   "Project_Name": None, 
                   "Time_Format": {"precision":3, "unit":"1us"},
                   "Module_Name": self.name,
                   "DUT": self.ports,
                   "Tool_Versions": None,
                   "Description": None,
                   "Timescale": "1ns / 1ps",
                   "Target_Devices": None,
                   "Company": None,
                   "Test_Vectors": self.vecs,
                   "Wait_Conditions": self.waitConditions
                   }
        
        return json.dumps(retDict, indent=4)


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
   

    axisIn_desc = {"name":"axisIn", "direction":"slave", "channels": [
                                                        {"name":"data", "type": "tdata", "size": 64},
                                                        {"name":"keep", "type": "tkeep"},
                                                        {"name":"valid", "type": "tvalid"},
                                                        {"name":"ready", "type": "tready"},
                                                        {"name":"last", "type": "tlast"},
                                                        ]
                                                                            
                }
    
    axisIn = axis( axisIn_desc)
    retList = axisIn.binToStream(dataArray, None)

    sec = ParallelSection()


    sec.addWait("mem_ready", "wait(mem_ready);")
    sec.addMacro("INIT_SIGNALS")
    sec.addDelay("40ns")
    sec.addBurst(retList)
    testVector0 = TestVector()
    testVector0.addSection(sec)

    module = Module('top_sim')
    module.addPort(axisIn_desc)
    module.addVec(testVector0)

    print module.getJSON()
