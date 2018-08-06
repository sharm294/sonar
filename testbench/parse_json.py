import os
import sys
import json
import re

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

def main(mode, filepath):

    if mode == "0":
        repoPath = os.environ.get('SHOAL_PATH')
        if repoPath is None:
            print("Error: SHOAL_PATH not defined in env")
            exit(-1)
        testFileName = repoPath + filepath
    else:
        testFileName = filepath
    if not os.path.isfile(testFileName):
        print("Error: File " + testFileName + " does not exist")
        exit(-2)

    tempFileName = testFileName.replace('.json', '_out.json')
    if os.path.isfile(tempFileName):
        print("Warning: overwriting existing file " + tempFileName)
    fRaw_commented = open(testFileName, "r")
    fTmp = open(tempFileName, "w+")

    fRaw = commentRemover(fRaw_commented.read())
    # fTmp.write(fRaw)
    rawData = json.loads(fRaw)

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
                            newDataSeq['sequential'].append(statement)
                        index+=1
                    loopFound = True
                else:
                    newDataSeq['sequential'].append(packet)
            newData['concurrent'].append(newDataSeq)
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
                                    packetTmp['payload'].append(statement)
                                index+=1
                        else:
                            packetTmp['payload'].append(word)
                    newDataSeq['sequential'].append(packetTmp)
                else:
                    newDataSeq['sequential'].append(packet)
                innerLoopFound = False
            newData['concurrent'].append(newDataSeq)
        rawData = newData.copy()
        if loopFound:
            newData = {}
            newData['concurrent'] = []

    # replace all hex numbers
    for block in rawData['concurrent']:
        for packet in block['sequential']:
            for word in packet['payload']:
                if not isinstance(word['data'], (int, long)):
                    if word['data'][:2] == "0x":
                        word['data'] = int(word['data'], 16)
                    else:
                        if word['data'][:2] == "0b":
                            word['data'] = int(word['data'], 2)
                        else:
                            word['data'] = int(word['data'],10)

    # replace all the keep values
    for block in rawData['concurrent']:
        for packet in block['sequential']:
            for word in packet['payload']:
                if 'keep' in word and not isinstance(word['data'], (int, long)):
                    if word['keep'] == "ALL":
                        word['keep'] = ((packet['width'] / 8) ** 2) - 1
                    else:
                        if word['keep'][:2] == "0x":
                            word['keep'] = int(word['data'], 16)
                        else:
                            word['keep'] = int(word['keep'],10)

    json.dump(newData, fTmp, indent=2, sort_keys=False)

if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print("Usage: python parse_json.py [mode] [filename]")
        print("  Mode: 0 - use relative path from Shoal repo root")
        print("        1 - use absolute file path")
        print("  Filename: JSON file to parse")
        exit(1)

    main(sys.argv[1], sys.argv[2])