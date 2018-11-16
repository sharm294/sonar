import os
import json
import sys

from include.utilities import printError
from include.utilities import trimFinalLine
from include.utilities import getFilePath
from include.utilities import sonar_types
from include.utilities import getInterface
from parse import parseJSON

################################################################################
### calculateSeeks ###
# This function repeats over the generated data file for systemverilog and 
# calculates the character counts for the different packets/parallel sections so 
# the fseek function can work properly during readback. It's repeated until all 
# the values converge to a static value.
def calculateSeeks(testData_sv, repeatCount, updateStr, seekStr, countStr, \
    converged):
    i = 0
    while i < repeatCount:
        charCount = 0
        continueCount = 0
        sectionFound = False
        continueCount2 = 0
        indexToEdit = 0
        oldSize = 0
        updated = False
        currentSectionCount = 0
        cumulativeSectionCount = 0
        for index, line in enumerate(testData_sv,0):
            charCount += len(line)
            if updateStr is not None and line.startswith(updateStr):
                currentSectionCount = int(line.split()[2]) #store the # of sections
                cumulativeSectionCount += currentSectionCount
            elif line.startswith(seekStr) and not sectionFound:
                if continueCount2 < i:
                    continueCount2 += 1
                else:
                    oldSize = int(line.split()[2])
                    sectionFound = True
                    updated = True
                    indexToEdit = index
            elif line.startswith(countStr) and sectionFound and updated:
                # This is needed to handle that there will be multiple parallel
                # sections for each test vector and to ignore the first set(s) 
                # when looking at the next set
                # if cumulativeSectionCount - currentSectionCount > 0:
                #     modulo = cumulativeSectionCount - currentSectionCount
                # else:
                #     modulo = repeatCount

                # if continueCount < i % (modulo):
                #     continueCount += 1
                if cumulativeSectionCount - currentSectionCount > 0:
                    modulo = i - cumulativeSectionCount + currentSectionCount
                else:
                    modulo = i
                
                if continueCount < modulo:
                    continueCount += 1
                else:
                    #account for new line characters and remove current line
                    sizeDiff = index - len(line) + charCount
                    if oldSize != sizeDiff:
                        converged = False
                    testData_sv[indexToEdit] = seekStr + " " + str(sizeDiff)
                    i += 1
                    continueCount = 0
                    updated = False
                    # break
    return testData_sv, converged

################################################################################
### writeLine_c ###
# This function writes a single line of the c data file
def writeLine_c(dataFile_c, packet):
    if 'type' in packet:
        packetType = packet['type']
        if packetType not in sonar_types and not packetType.startswith("signal"):
            currInterface = getInterface(packetType)
            if currInterface is None:
                exit(1)
            dataFile_c.write(currInterface.write_c(packet))
        elif packetType == 'end':
            # NULL is added as a dummy string
            dataFile_c.write("end " + str(packet['id']) + " NULL 1 0 " + \
            str(packet['value']) + "\n")
        elif packetType == 'timestamp':
            dataFile_c.write("timestamp " + str(packet['interface']) + " " + \
                "NULL 1 0 " + str(packet['value']) + "\n")
        # TODO Supporting signal assignment in C++ became more complex so it's
        # TODO just been commented out of the final C++ data file but there are 
        # TODO hooks in Sonar to partially handle it (i.e. signal_* types)
        # elif packetType == 'signal':
        #     dataFile_c.write(str(packet['interface']) + " " + str(packet['id']) + \
        #         " NULL 1 0 " + str(packet['value']) + "\n")
        elif packetType == 'display':
            dataFile_c.write("display " + str(packet['interface']) + " " + \
                "NULL 1 0 " + str(packet['value']) + "\n")
    else:
        for packet2 in packet:
            writeLine_c(dataFile_c, packet2)

################################################################################
### writeLine_sv ###
# This function writes a single line of the systemverilog data file
def writeLine_sv(dataFile_sv, packet):
    if 'type' in packet:
        packetType = packet['type']
        if packetType not in sonar_types and not packetType.startswith("signal"):
            currInterface = getInterface(packet['type'])
            if currInterface is None:
                exit(1)
            line = currInterface.write_sv(packet)
            if line != "":
                dataFile_sv.append(line)
        elif packetType == 'wait':
            dataFile_sv.append("wait " + str(packet['interface']) + " " + \
                str(1) + " " + str(packet['value']))
        elif packetType.startswith('signal'): # hook for different signal types
            dataFile_sv.append("signal " + str(packet['interface']) + " " + \
                str(1) + " " + str(packet['value']))
        elif packetType == 'delay':
            dataFile_sv.append("delay " + str(packet['interface']) + " " + \
                str(1) + " " + str(packet['value']))
        elif packetType == 'display':
            dataFile_sv.append("display " + str(packet['interface']) + " " + \
                str(1) + " " + str(packet['value']))
        elif packetType == 'flag':
            dataFile_sv.append("flag " + str(packet['interface']) + " " + \
                str(1) + " " + str(packet['value']))
        elif packetType == 'timestamp':
            dataFile_sv.append("timestamp " + str(packet['interface']) + " " + \
                str(1) + " " + str(packet['value']))
        elif packetType == 'end':
            dataFile_sv.append("end " + str(packet['interface']) + " " + \
                str(1) + " " + str(packet['value']))
        else:
            printError(1, "Unhandled type in writeLine_sv: "+ packetType)
            exit(1)
    else:
        for packet2 in packet:
            writeLine_sv(dataFile_sv, packet2)

################################################################################
### generate ###
# This function generates the data files for C and systemverilog testbenches.
def generate(mode, modeArg, filepath, languages):

    if languages == "all":
        enable_SV = True
        enable_C = True
    elif languages == "sv":
        enable_SV = True
        enable_C = False
    else:
        printError(1, "Unsupported language: " + languages)
        exit(1)

    # sanitize the JSON and continue processing
    outFileName = parseJSON(mode, modeArg, filepath)
    try:
        with open(outFileName, "r") as outFile:
            testFile = json.load(outFile)
    except ValueError, e:
        printError(1, "Unable to open JSON file. See errors above")
        exit(1)

    pathTuple = os.path.split(outFileName)
    currentDirectory = pathTuple[0] + "/" + pathTuple[1].replace('_out.json', \
        '')

    filename_c = currentDirectory + "_c.dat"
    filename_sv = currentDirectory + "_sv.dat"
    if enable_C:
        dataFile_c = open(filename_c, "w+")
    dataFile_sv = open(filename_sv, "w+")

    absTestVectorCount = testFile['count']
    absParallelSectionCount = 0

#------------------------------------------------------------------------------#
# Generate data files

    testData_sv = []
    testData_sv.append("TestVector count " + str(testFile['count']))
    for seek in testFile['seek']:
        testData_sv.append("TestVector seek " + str(seek))

    for testVector in testFile['data']:
        if 'count' in testVector:
            testData_sv.append("ParallelSection count " + \
                str(testVector['count']))
        if 'seek' in testVector:
            for seek in testVector['seek']:
                testData_sv.append("ParallelSection seek " + str(seek))
                absParallelSectionCount += 1
        for parallelSection in testVector['data']:
            if 'count' in parallelSection:
                testData_sv.append("Packet count " + \
                    str(parallelSection['count']))
            if 'seek' in parallelSection:
                testData_sv.append("Packet seek " + \
                    str(parallelSection['seek']))
            for packet in parallelSection['data']:
                if enable_C:
                    writeLine_c(dataFile_c, packet)
                writeLine_sv(testData_sv, packet)

#------------------------------------------------------------------------------#

    # resolve seek sizes for systemverilog data file
    converged1 = False
    converged2 = False
    while not (converged1 and converged2):
        converged1 = True
        converged2 = True
        testVectorCount = 0
        testData_sv, converged1 = calculateSeeks(testData_sv, \
            absTestVectorCount, None, "TestVector seek", \
            "ParallelSection count", converged1)
        parallelSectionCount = 0
        testData_sv, converged2 = calculateSeeks(testData_sv, \
            absParallelSectionCount, "ParallelSection count", \
            "ParallelSection seek", "Packet count", converged2)

    for line in testData_sv:
        dataFile_sv.write(line + "\n")          

    # remove final new line character
    if enable_C:
        trimFinalLine(dataFile_c)
    trimFinalLine(dataFile_sv)

    # append a finish tag to the C data file that is used to break out of an 
    # infinite while loop in the C testbench. ap_uint wasn't properly handling 
    # the case where there's nothing to read (i.e. end of file) so this is used 
    # to exit instead of relying on when we can no longer read data.
    if enable_C:
        dataFile_c.write("\nfinish NULL NULL 0 0")
        dataFile_c.close()
    
    dataFile_sv.close()

################################################################################

if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "-h" or arg == "--help":
            print("Usage: python generate.py mode modeArg filename")
            print("  mode: env - use relative path from an environment variable")
            print("        path - use relative path from a string")
            print("        absolute - use absolute filepath")
            print("  modeArg: environment variable or path string. None otherwise")
            print("  filename: JSON file to parse")

    if (len(sys.argv) == 4):
        generate(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Incorrect number of arguments. Use -h or --help")