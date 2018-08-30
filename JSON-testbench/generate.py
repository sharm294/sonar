import os
import json
import sys

from testbench.utilities import printError
from testbench.utilities import trimFinalLine
from testbench.utilities import getFilePath
from testbench.parse_json import parseJSON

def calculateSeeks(testData_sv, repeatCount, updateStr, seekStr, countStr, converged):
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
                currentSectionCount = int(line.split()[2])
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
                if cumulativeSectionCount - currentSectionCount > 0:
                    modulo = cumulativeSectionCount - currentSectionCount
                else:
                    modulo = repeatCount
                if continueCount < i % (modulo):
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
    return testData_sv, converged

def writeLine_c(dataFile_c, packet):
    if 'type' in packet:
        packetType = packet['type']
        if packetType == 'axis':
            for word in packet['payload']:
                dataFile_c.write(packet['interface']+ " " + \
                    '0x{0:0{1}X}'.format(word['data'], 8) + " " + \
                    str(word['last']) + " " + str(word['callTB']) + " " + \
                    str(word['keep']) + " " + str(word['id'])+"\n")
        elif packetType == 'end':
            dataFile_c.write("end " + " " + \
                '0x{0:0{1}X}'.format(packet['value'], 8) + " 0 0 0")
    else:
        for packet2 in packet:
            writeLine_c(dataFile_c, packet2)

def writeLine_sv(dataFile_sv, packet):
    if 'type' in packet:
        packetType = packet['type']
        if packetType == 'axis':
            for word in packet['payload']:
                if word['keep'] < 1024: #exclude debug statements
                    dataFile_sv.append(packetType + " " + packet['interface']+ " " + \
                        str(word['data']) + " " + \
                        str(word['last']) + " " + \
                        str(word['keep']))
        elif packetType == 'wait':
            dataFile_sv.append("wait " + str(packet['interface']) + " " + \
                str(packet['value']) + " 0 0")
        elif packetType == 'signal':
            dataFile_sv.append("signal " + str(packet['interface']) + " " + \
                str(packet['value']) + " 0 0")
        elif packetType == 'delay':
            dataFile_sv.append("delay " + str(packet['interface']) + " " + \
                str(packet['value']) + " 0 0")
        elif packetType == 'end':
            dataFile_sv.append("end " + str(packet['interface']) + " " + \
                str(packet['value']) + " 0 0")
    else:
        for packet2 in packet:
            writeLine_sv(dataFile_sv, packet2)

def generate(mode, filepath):

    parseJSON(mode, filepath)

    testFileName = getFilePath(mode, filepath)
    if testFileName is None:
        exit(1)

    pathTuple = os.path.split(testFileName)
    if not os.path.exists(pathTuple[0] + "/build/"):
        os.makedirs(pathTuple[0] + "/build/")
    outFileName = pathTuple[0] + "/build/" + pathTuple[1].replace('.json', '_out.json')

    try:
        testFile = json.load(open(outFileName, "r"))
    except ValueError, e:
        printError(1, "Unable to open JSON file. See errors above")
        exit(1)

    currentDirectory = pathTuple[0] + "/build/" + pathTuple[1].replace('.json', '')

    filename_c = currentDirectory + "_c.dat"
    filename_sv = currentDirectory + "_sv.dat"
    dataFile_c = open(filename_c, "w+")
    dataFile_sv = open(filename_sv, "w+")

    absTestVectorCount = testFile['count']
    absParallelSectionCount = 0

    testData_sv = []
    testData_sv.append("TestVector count " + str(testFile['count']))
    for seek in testFile['seek']:
        testData_sv.append("TestVector seek " + str(seek))

    for testVector in testFile['data']:
        if 'count' in testVector:
            testData_sv.append("ParallelSection count " + str(testVector['count']))
        if 'seek' in testVector:
            for seek in testVector['seek']:
                testData_sv.append("ParallelSection seek " + str(seek))
                absParallelSectionCount += 1
        for parallelSection in testVector['data']:
            if 'count' in parallelSection:
                testData_sv.append("Packet count " + str(parallelSection['count']))
            if 'seek' in parallelSection:
                testData_sv.append("Packet seek " + str(parallelSection['seek']))
            for packet in parallelSection['data']:
                writeLine_c(dataFile_c, packet)
                writeLine_sv(testData_sv, packet)

    #resolve test vector seek sizes
    converged = False
    while not converged:
        converged = True
        testVectorCount = 0
        testData_sv, converged = calculateSeeks(testData_sv, \
            absTestVectorCount, None, "TestVector seek", \
            "ParallelSection count", converged)
        parallelSectionCount = 0
        testData_sv, converged = calculateSeeks(testData_sv, \
            absParallelSectionCount, "ParallelSection count", \
            "ParallelSection seek", "Packet count", converged)

    for line in testData_sv:
        dataFile_sv.write(line + "\n")          

    trimFinalLine(dataFile_c)
    trimFinalLine(dataFile_sv)

    dataFile_c.close()
    dataFile_sv.close()

if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "-h" or arg == "--help":
            print("Usage: python generate.py mode filename")
            print("Arguments: ")
            print("  mode: 0 - use relative path from Shoal repo root")
            print("        1 - use absolute file path")
            print("  filename - name of the file to parse")
            exit(1)

    if (len(sys.argv) == 3):
        generate(sys.argv[1], sys.argv[2])
    else:
        print("Incorrect number of arguments. Use -h or --help")