import os
import json
import sys

from utilities import printError
from utilities import trimFinalLine
from utilities import getFilePath
from parse import parseJSON

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
            dataFile_c.write("end " + \
                '0x{0:0{1}X}'.format(packet['value'], 8) + " 0 0 0 " + 
                    str(packet['id'])+"\n")
    else:
        for packet2 in packet:
            writeLine_c(dataFile_c, packet2)

def writeLine_sv(dataFile_sv, packet):
    if 'type' in packet:
        packetType = packet['type']
        if packetType == 'axis':
            for word in packet['payload']:
                if word['keep'] != 0: #exclude debug statements
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
        elif packetType == 'timestamp':
            dataFile_sv.append("timestamp " + str(packet['interface']) + " " + \
                str(packet['value']) + " 0 0")
        elif packetType == 'end':
            dataFile_sv.append("end " + str(packet['interface']) + " " + \
                str(packet['value']) + " 0 0")
    else:
        for packet2 in packet:
            writeLine_sv(dataFile_sv, packet2)

def generate(mode, modeArg, filepath):

    outFileName = parseJSON(mode, modeArg, filepath)
    try:
        with open(outFileName, "r") as outFile:
            testFile = json.load(outFile)
    except ValueError, e:
        printError(1, "Unable to open JSON file. See errors above")
        exit(1)

    pathTuple = os.path.split(outFileName)
    currentDirectory = pathTuple[0] + "/" + pathTuple[1].replace('_out.json', '')

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

    dataFile_c.write("\nfinish 0 0 0 0 0") #fixes reading fixed point reading issue

    dataFile_c.close()
    dataFile_sv.close()

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