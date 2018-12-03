import os
import sys
import json
import re

from .include.strToInt import strToInt
from .include.utilities import extractNumber
from .include.utilities import printError
from .include.utilities import printWarning
from .include.utilities import getFilePath
from .include.utilities import stripFileName
from .include.utilities import sonar_types
from .include.utilities import getInterface

################################################################################
### expandLoops ###
# This function expands the loop data structure for outer and inner loops. It 
# calls an 'expandingFunction' which is one of outerLoops or innerLoops.

def expandLoops(rawData, expandingFunction):
    newData = {}
    newData['data'] = []
    loopFound = True
    while loopFound:
        loopFound = False
        for testVector in rawData['data']:
            newData_testVector = {}
            newData_testVector['data'] = []
            if 'data' not in testVector:
                print('The data key not found in dict:')
                print(testVector)
                raise KeyError
            for parallelSection in testVector['data']:
                newData_parallelSection = {}
                newData_parallelSection['data'] = []
                if 'data' not in parallelSection:
                    print('\nFATAL ERROR\n')
                    print(json.dumps(parallelSection, indent=2))
                    raise KeyError('The data key not found in dict')
                for packet in parallelSection['data']:
                    newData_parallelSection['data'], loopFound = expandingFunction(packet, \
                        newData_parallelSection['data'], loopFound)
                newData_testVector['data'].append(newData_parallelSection)
            newData['data'].append(newData_testVector)
        rawData = newData.copy()
        if loopFound:
            newData = {}
            newData['data'] = []

    return rawData

################################################################################
### convertPayload ###
# This function converts each key in each packet in an interface payload to an
# integer.

def convertPayload(packet):
    if 'type' in packet:
        if 'payload' in packet:
            for payload in packet['payload']:
                for key in payload:
                    if not isinstance(payload[key], (int, long)):
                        if payload[key][:1] == "{":
                            payload[key] = strToInt(payload[key])
                        else:
                            payload[key] = extractNumber(payload[key])
    else:
        for packet2 in packet:
            addID(packet2)

################################################################################
### addID ###
# This function appends an increasing ID number to each packet in an interface 
# payload. This needs to occur after all inner loops have been expanded.

def addID(packet):
    if 'type' in packet:
        if 'payload' in packet:
            for index, word in enumerate(packet['payload']):
                word['id'] = packet['id'] + str(index)
    else:
        for packet2 in packet:
            addID(packet2)

################################################################################
### convertValue ###
# This function converts the 'value' key in a packet to an integer.

def convertValue(packet):
    if 'type' in packet:
        if 'value' in packet:
            if not isinstance(packet['value'], (int, long)):
                if packet['value'][:1] == "{":
                    packet['value'] = strToInt(packet['value'])
                else:
                    packet['value'] = extractNumber(packet['value'])
    else:
        for packet2 in packet:
            convertData(packet2)

################################################################################
### outerLoops ###
# This function expands the loop structure found around individual packets. It 
# returns the expanded dictionary.
# 
# Note: this function may be removed in later versions. It's less useful than 
# originally envisioned and not supported in a YAML configuration file.

def outerLoops(packet, newDataSeq, loopFound):
    if 'type' in packet: #this is an object
        newDataSeq, loopFound = resolveOuterLoop(packet, newDataSeq, loopFound)
    else: #this is an array
        newDataSeq2 = []
        for packet2 in packet:
            newDataSeq2, loopFound = outerLoops(packet2, newDataSeq2, loopFound)
        newDataSeq.append(newDataSeq2)
    return newDataSeq, loopFound

#------------------------------------------------------------------------------#

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

################################################################################
### innerLoops ###
# This function expands the loop structure found inside the payload array in an 
# interface. It returns the expanded dictionary.

def innerLoops(packet, newDataSeq, loopFound):
    if 'type' in packet: #this is an object
        newDataSeq,loopFound = resolveInnerLoop(packet, newDataSeq, loopFound)
    else: #this is an array
        newDataSeq2 = []
        for packet2 in packet:
            newDataSeq2,loopFound = innerLoops(packet2, newDataSeq2, loopFound)
        newDataSeq.append(newDataSeq2)
    return newDataSeq, loopFound

#------------------------------------------------------------------------------#

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

################################################################################
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

################################################################################
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
# Return: Path of file created. Writes the new valid JSON file in the 
#   same directory as the source JSON file
#TODO tie printing warnings to a verbosity flag or a quiet flag
def parseJSON(mode, modeArg, filepath):

    testFileName = getFilePath(mode, modeArg, filepath)
    if testFileName is None:
        exit(1)

    pathTuple = os.path.split(testFileName)
    tempFileName = pathTuple[0] + "/" + pathTuple[1].replace('.json', '_out.json')
    # if os.path.isfile(tempFileName):
    #     if mode == "env":
    #         message = "Overwriting existing file $" + modeArg + stripFileName(mode, modeArg, tempFileName)
    #     else:
    #         message = "Overwriting existing file $" + tempFileName
    #     printWarning(message)
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

    rawData = expandLoops(rawData, outerLoops)

    rawData = expandLoops(rawData, innerLoops)

    # add count and seek values that are used with systemverilog testbenches
    for testVector in rawData['data']:
        for parallelSection in testVector['data']:
            sv_count = 0
            for packet in parallelSection['data']:
                if packet['type'] in sonar_types or packet['type'].startswith("signal"):
                    sv_count += 1
                elif 'interface' in packet:
                    currInterface = getInterface(packet['type'])
                    if currInterface is None:
                        exit(1)
                    svPacket = currInterface.count(packet)
                    sv_count += svPacket
                else:
                    printError(1, "Unknown packet type: " + packet['type'])
                    exit(1)
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
                packetType = packet['type']
                if packetType not in sonar_types and not packetType.startswith("signal"):
                    currInterface = getInterface(packet['type'])
                    currInterface.convert(packet)
                convertValue(packet)
                convertPayload(packet)
                addID(packet) # add ID tags to each payload

    json.dump(rawData, fTmp, indent=2, sort_keys=False)
    
    fRaw_commented.close()
    fTmp.close()
    return tempFileName

################################################################################

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