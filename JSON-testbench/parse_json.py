import os
import sys
import json
import re

from utilities import strToInt
from utilities import extractNumber
from utilities import printError
from utilities import printWarning
from utilities import getFilePath

def expandLoops(rawData, expandingFunction):
    newData = {}
    newData['data'] = []
    loopFound = True
    while loopFound:
        loopFound = False
        for testVector in rawData['data']:
            newData_testVector = {}
            newData_testVector['data'] = []
            for parallelSection in testVector['data']:
                newData_parallelSection = {}
                newData_parallelSection['data'] = []
                for packet in parallelSection['data']:
                    newData_parallelSection['data'], loopFound = expandingFunction(packet, \
                        newData_parallelSection['data'], loopFound)
                newData_testVector['data'].append(newData_parallelSection)
            newData['data'].append(newData_testVector)
        rawData = newData.copy()
        if loopFound:
            newData = {}
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
        if packetType == 'axis':
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

### commentRemover ###
# This function removes all C-style comments (// and /* */) from a JSON file.
# Since comments are not allowed in JSON, they must be removed initially. This 
# function is adapted from https://gist.github.com/ChunMinChang/88bfa5842396c1fbbc5b
#
# Arguments:
#   text: the read text from a file
#
# Return: the text with all comments replaced with spaces

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

### parseJSON ###
# This function parses and expands the user-specified JSON file into a valid,
# generic JSON file that can be used to generate test data files. The generated 
# JSON file is free of comments, integer strings and other user abstractions 
# available in the user JSON
#
# Arguments:
#   mode: must be one of "env", "path", or "absolute". 
#       - "env" considers modeArg as an environment variable and appends the 
#           filepath to it
#       - "path" considers modeArg as a path and appends the filepath to it
#       - "absolute" ignores modeArg and uses the filepath alone
#   modeArg: a string argument used in conjunction with mode
#   filepath: a string argument for the file to check
#
# Return: N/A. Writes the new valid JSON file in a build/ subdirectory in the 
#   same directory as the source JSON file
#TODO tie printing warnings to a verbosity flag or a quiet flag
def parseJSON(mode, modeArg, filepath):

    testFileName = getFilePath(mode, modeArg, filepath)
    if testFileName is None:
        exit(1)

    pathTuple = os.path.split(testFileName)
    if not os.path.exists(pathTuple[0] + "/build/"):
        os.makedirs(pathTuple[0] + "/build/")
    tempFileName = pathTuple[0] + "/build/" + pathTuple[1].replace('.json', '_out.json')
    if os.path.isfile(tempFileName):
        message = "Overwriting existing file " + filepath
        printWarning(message)
    fRaw_commented = open(testFileName, "r")
    fTmp = open(tempFileName, "w+")

    fRaw = commentRemover(fRaw_commented.read())
    try:
        rawData = json.loads(fRaw)
    except ValueError, e:
        fTmp.write(fRaw)
        message = "Invalid JSON file. Use " + filepath + \
            " to find errors and fix source file."
        printError(3, message)
        exit(3)

    expandLoops(rawData, outerLoops)

    expandLoops(rawData, innerLoops)

    # add count and seek values that are used with systemverilog testbenches
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

    for testVector in rawData['data']:
        for parallelSection in testVector['data']:
            for packet in parallelSection['data']:
                convertData(packet) # replace all string numbers in data
                convertKeep(packet) # replace all the keep values
                addID(packet) # add ID tags to each payload

    json.dump(rawData, fTmp, indent=2, sort_keys=False)

if __name__ == "__main__":

    if (len(sys.argv) != 4):
        print("Usage: python parse_json.py mode modeArg filename")
        print("  mode: env - use relative path from an environment variable")
        print("        path - use relative path from a string")
        print("        absolute - use absolute filepath")
        print("  modeArg: environment variable or path string. None otherwise")
        print("  filename: JSON file to parse")
        exit(1)

    parseJSON(sys.argv[1], sys.argv[2], sys.argv[3])