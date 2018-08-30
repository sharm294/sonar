import os
import sys
import json
import re

from testbench.utilities import strToInt
from testbench.utilities import extractNumber
from testbench.utilities import printError
from testbench.utilities import printWarning
from testbench.utilities import stripFileName
from testbench.utilities import getFilePath

def expandLoops(rawData, expandingFunction):
    newData = {}
    # newData['seek'] = rawData['seek']
    # newData['count'] = rawData['count']
    newData['data'] = []
    loopFound = True
    while loopFound:
        loopFound = False
        for testVector in rawData['data']:
            newData_testVector = {}
            # if 'count' in testVector:
            #     newData_testVector['count'] = testVector['count']
            # if 'seek' in testVector:
            #     newData_testVector['seek'] = testVector['seek']
            newData_testVector['data'] = []
            for parallelSection in testVector['data']:
                newData_parallelSection = {}
                # if 'count' in parallelSection:
                #     newData_testVector['count'] = parallelSection['count']
                # if 'seek' in parallelSection:
                #     newData_testVector['seek'] = parallelSection['seek']
                newData_parallelSection['data'] = []
                for packet in parallelSection['data']:
                    newData_parallelSection['data'], loopFound = expandingFunction(packet, \
                        newData_parallelSection['data'], loopFound)
                newData_testVector['data'].append(newData_parallelSection)
            newData['data'].append(newData_testVector)
        rawData = newData.copy()
        if loopFound:
            newData = {}
            # newData['seek'] = rawData['seek']
            # newData['count'] = rawData['count']
            newData['data'] = []
    rawData = newData.copy()

def addID(packet):
    if 'type' in packet:
        packetType = packet['type']
        if packetType == 'axis' or packetType == 'csim':
            for index, word in enumerate(packet['payload']):
                word['id'] = packet['id'] + str(index)
    else:
        for packet2 in packet:
            addID(packet2)

def convertKeep(packet):
    if 'type' in packet:
        packetType = packet['type']
        if packetType == 'axis' or packetType == 'csim':
            for word in packet['payload']:
                if 'keep' in word and not isinstance(word['keep'], (int, long)):
                    if word['keep'] == "ALL":
                        word['keep'] = (2 ** (packet['width'] / 8)) - 1
                    else:
                        word['keep'] = extractNumber(word['keep'])
    else:
        for packet2 in packet:
            convertKeep(packet2)    

def convertData(packet):
    if 'type' in packet:
        packetType = packet['type']
        if packetType == 'axis' or packetType == 'csim':
            for word in packet['payload']:
                if not isinstance(word['data'], (int, long)):
                    if word['data'][:1] == "{":
                        word['data'] = strToInt(word['data'])
                    else:
                        word['data'] = extractNumber(word['data'])
        elif packetType == 'wait':
            if not isinstance(packet['value'], (int, long)):
                if packet['value'][:1] == "{":
                    packet['value'] = strToInt(packet['value'])
                else:
                    packet['value'] = extractNumber(packet['value'])
    else:
        for packet2 in packet:
            convertData(packet2)

def outerLoops(packet, newDataSeq, loopFound):
    if 'type' in packet: #this is an object
        newDataSeq, loopFound = resolveOuterLoop(packet, newDataSeq, loopFound)
    else: #this is an array
        newDataSeq2 = []
        for packet2 in packet:
            newDataSeq2, loopFound = outerLoops(packet2, newDataSeq2, loopFound)
        newDataSeq.append(newDataSeq2)
    return newDataSeq, loopFound    

def resolveOuterLoop(packet, sequence, loopFound):
    if packet['type'] == "loop":
        index = packet['start']
        while index < packet['end']:
            for statement in packet['body']:
                sequence.append(statement.copy())
            index+=1
        loopFound = True
    else:
        sequence.append(packet.copy())

    return sequence, loopFound

def innerLoops(packet, newDataSeq, loopFound):
    if 'type' in packet: #this is an object
        newDataSeq,loopFound = resolveInnerLoop(packet, newDataSeq, loopFound)
    else: #this is an array
        newDataSeq2 = []
        for packet2 in packet:
            newDataSeq2,loopFound = innerLoops(packet2, newDataSeq2, loopFound)
        newDataSeq.append(newDataSeq2)
    return newDataSeq, loopFound

def resolveInnerLoop(packet, sequence, loopFound):
    innerLoopFound = False
    if 'payload' in packet:
        for word in packet['payload']:
            if 'loop' in word:
                loopFound = True
                innerLoopFound = True
        if innerLoopFound:
            packetTmp = packet.copy()
            del packetTmp['payload']
            packetTmp['payload'] = []
            for word in packet['payload']:
                if 'loop' in word:
                    index = word['loop']['start']
                    while index < word['loop']['end']:
                        for statement in word['loop']['body']:
                            packetTmp['payload'].append(statement.copy())
                        index+=1
                else:
                    packetTmp['payload'].append(word.copy())
            sequence.append(packetTmp.copy())
        else:
            sequence.append(packet.copy())
    else:
        sequence.append(packet.copy())
    return sequence, loopFound

# taken from https://gist.github.com/ChunMinChang/88bfa5842396c1fbbc5b
def commentRemover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def parseJSON(mode, filepath):

    testFileName = getFilePath(mode, filepath)
    if testFileName is None:
        exit(1)

    pathTuple = os.path.split(testFileName)
    if not os.path.exists(pathTuple[0] + "/build/"):
        os.makedirs(pathTuple[0] + "/build/")
    tempFileName = pathTuple[0] + "/build/" + pathTuple[1].replace('.json', '_out.json')
    if os.path.isfile(tempFileName):
        message = "Overwriting existing file " + stripFileName(tempFileName)
        printWarning(message)
    fRaw_commented = open(testFileName, "r")
    fTmp = open(tempFileName, "w+")

    fRaw = commentRemover(fRaw_commented.read())
    try:
        rawData = json.loads(fRaw)
    except ValueError, e:
        fTmp.write(fRaw)
        message = "Invalid JSON file. Use " + stripFileName(tempFileName) + \
            " to find errors and fix source file."
        printError(3, message)
        exit(3)

    expandLoops(rawData, outerLoops)

    expandLoops(rawData, innerLoops)

    # add count and seek values
    for testVector in rawData['data']:
        for parallelSection in testVector['data']:
            sv_count = 0
            for packet in parallelSection['data']:
                if packet['type'] == "delay" or packet['type'] == "wait" or \
                    packet['type'] == "signal" or packet['type'] == 'end':
                    sv_count += 1
                elif packet['type'] == 'axis':
                    svPacket = False
                    for payload in packet['payload']:
                        if not payload['data'].startswith("0s"):
                            svPacket = True
                    if svPacket:
                        sv_count += 1
            if sv_count > 0:
                parallelSection['count'] = sv_count

    for testVector in rawData['data']:
        sv_count = 0
        for parallelSection in testVector['data']:
            if 'count' in parallelSection:
                sv_count += 1
        if sv_count > 0:
            testVector['count'] = sv_count
            testVector['seek'] = [0] * sv_count

    sv_count = 0
    for testVector in rawData['data']:
        if 'count' in testVector:
            sv_count += 1
    if sv_count > 0:
        rawData['count'] = sv_count
        rawData['seek'] = [0] * sv_count

    # replace all hex numbers in data
    for testVector in rawData['data']:
        for parallelSection in testVector['data']:
            for packet in parallelSection['data']:
                convertData(packet)

    # replace all the keep values
    for testVector in rawData['data']:
        for parallelSection in testVector['data']:
            for packet in parallelSection['data']:
                convertKeep(packet)

    # add id tags to each payload
    for testVector in rawData['data']:
        for parallelSection in testVector['data']:
            for packet in parallelSection['data']:
                addID(packet)

    json.dump(rawData, fTmp, indent=2, sort_keys=False)

if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print("Usage: python parse_json.py mode filename")
        print("  Mode: 0 - use relative path from Shoal repo root")
        print("        1 - use absolute file path")
        print("  Filename: JSON file to parse")
        exit(1)

    parseJSON(sys.argv[1], sys.argv[2])