import os
import sys
import json
import re

from testbench.utilities import strToInt
from testbench.utilities import extractNumber
from testbench.utilities import printError
from testbench.utilities import printWarning
from testbench.utilities import stripFileName

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

    if mode == "0":
        repoPath = os.environ.get('SHOAL_PATH')
        if repoPath is None:
            printError(1, "SHOAL_PATH not defined in env")
            exit(1)
        testFileName = repoPath + filepath
    else:
        testFileName = filepath
    if not os.path.isfile(testFileName):
        message = "File " + stripFileName(testFileName) + " does not exist"
        printError(2, message)
        exit(2)

    pathTuple = os.path.split(testFileName)
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

    newData = {}
    newData['concurrent'] = []

    # expand all outer loops
    loopFound = True
    while loopFound:
        loopFound = False
        for block in rawData['concurrent']:
            newDataSeq = {}
            newDataSeq['sequential'] = []
            for packet in block['sequential']:
                if packet['type'] == "loop":
                    index = packet['start']
                    while index < packet['end']:
                        for statement in packet['body']:
                            newDataSeq['sequential'].append(statement.copy())
                        index+=1
                    loopFound = True
                else:
                    newDataSeq['sequential'].append(packet.copy())
            newData['concurrent'].append(newDataSeq.copy())
        rawData = newData.copy()
        if loopFound:
            newData = {}
            newData['concurrent'] = []

    rawData = newData.copy()
    newData = {}
    newData['concurrent'] = []

    # expand all inner loops
    loopFound = True
    while loopFound:
        loopFound = False
        innerLoopFound = False
        for block in rawData['concurrent']:
            newDataSeq = {}
            newDataSeq['sequential'] = []
            for packet in block['sequential']:
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
                    newDataSeq['sequential'].append(packetTmp.copy())
                else:
                    newDataSeq['sequential'].append(packet.copy())
                innerLoopFound = False
            newData['concurrent'].append(newDataSeq.copy())
        rawData = newData.copy()
        if loopFound:
            newData = {}
            newData['concurrent'] = []

    # replace all hex numbers
    for block in rawData['concurrent']:
        for packet in block['sequential']:
            for word in packet['payload']:
                if not isinstance(word['data'], (int, long)):
                    if word['data'][:1] == "{":
                        word['data'] = strToInt(word['data'])
                    else:
                       word['data'] = extractNumber(word['data'])

    # replace all the keep values
    for block in rawData['concurrent']:
        for packet in block['sequential']:
            for word in packet['payload']:
                if 'keep' in word and not isinstance(word['keep'], (int, long)):
                    if word['keep'] == "ALL":
                        word['keep'] = ((packet['width'] / 8) ** 2) - 1
                    else:
                        word['keep'] = extractNumber(word['keep'])

    # add id tags to each payload
    for block in rawData['concurrent']:
        for packet in block['sequential']:
            for index, word in enumerate(packet['payload']):
                word['id'] = packet['id'] + str(index)

    json.dump(rawData, fTmp, indent=2, sort_keys=False)

if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print("Usage: python parse_json.py [mode] [filename]")
        print("  Mode: 0 - use relative path from Shoal repo root")
        print("        1 - use absolute file path")
        print("  Filename: JSON file to parse")
        exit(1)

    parseJSON(sys.argv[1], sys.argv[2])