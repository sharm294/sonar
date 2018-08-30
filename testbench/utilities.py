import sys
import os

def getFilePath(mode, filepath):
    if mode == "0":
        repoPath = getEnvironmentVar('SHOAL_PATH')
        if repoPath is None:
            return None
        else:
            testFileName = repoPath + filepath
    else:
        testFileName = filepath

    if not os.path.isfile(testFileName):
        message = "File " + stripFileName(testFileName) + " does not exist"
        printError(2, message)
        return None
    else:
        return testFileName

def trimFinalLine(filename):
    filename.seek(0, os.SEEK_END) #move to end of file
    pos = filename.tell()
    while pos > 0 and filename.read(1) != "\n": #traverse back until \n
        pos -= 1
        filename.seek(pos, os.SEEK_SET)

    if pos > 0: #if we're not at the start, delete chars ahead
        filename.seek(pos, os.SEEK_SET)
        filename.truncate()

def getEnvironmentVar(envVar):
    variable = os.environ.get(envVar)
    if variable is None:
        printError(1, envVar + " not defined in env")
        return None
    else:
        return variable

def stripFileName(filename):
    repoPath = getEnvironmentVar("SHOAL_PATH")
    if repoPath is None:
        return None
    
    localName = filename.replace(repoPath, '')
    return localName    

def printWarning(message):
    print("*** Warning *** : " + message)

def printError(errorCode, message):
    print("*** Fatal Error *** Code " + str(errorCode) + ": " + message)

def evalMacro(header, macro):
    import subprocess

    command = "g++ -I$SHOAL_PATH/share/include \
        -I$SHOAL_VIVADO_HLS -I$SHOAL_PATH/GASCore/include \
        $SHOAL_PATH/share/src/eval_macro.cpp -w \
        -include $SHOAL_PATH/" + header + " -DMACRO_VALUE=" + \
        macro + " -o $SHOAL_PATH/share/build/bin/eval_macro"

    subprocess.call(command, shell=True)
    return subprocess.check_output("$SHOAL_PATH/share/build/bin/eval_macro", shell=True)

def extractNumber(numberStr):
    if not isinstance(numberStr, (int, long)):
        if numberStr[:2] == "0x":
           number = int(numberStr, 16)
        elif numberStr[:2] == "0b":
            number = int(numberStr, 2)
        elif numberStr[:2] == "0s":
            if numberStr[2:] == "dbgPrint":
                number = 0
            elif numberStr[2:] == "dbgState":
                number = 1
            elif numberStr[2:] == "dbgContinue":
                number = 2
            else:
                printError(-1, "Unknown print 0s command: " + numberStr[2:])
                number = -1
        else:
            number = int(numberStr, 10)

        return number
    else:
        return int(numberStr, 10)

#This assumes the format {type,arg0,arg1,...,argn}
def strToInt(packet):
    packetArgs = packet[1:-1].split(",")
    intVal = 0

    if packetArgs[0] == "AMHeader":
        assert (len(packetArgs) == 7),"Invalid number of arguments for AMHeader"
        if ":" not in packetArgs[1]:
            argSrc = packetArgs[1]
            argDst = packetArgs[2]
            argPayload = packetArgs[3]
            argHandler = packetArgs[4]
            argPacketType = packetArgs[5]
            argArguments = packetArgs[6]
        else:
            for arg in packetArgs[1:]:
                argList = arg.split(":")
                if argList[0] == "src":
                    argSrc = argList[1]
                elif argList[0] == "dst":
                    argDst = argList[1]
                elif argList[0] == "payload":
                    argPayload = argList[1]
                elif argList[0] == "handler":
                    argHandler = argList[1]
                elif argList[0] == "type":
                    argPacketType = argList[1]
                elif argList[0] == "args":
                    argArguments = argList[1]
                else:
                    printError(1, "Invalid key for AMLongVector")
                    exit(1)
        
        src = extractNumber(argSrc)
        dst = extractNumber(argDst) << 16
        payload = extractNumber(argPayload) << 32
        handler = extractNumber(argHandler) << 44
        packetType = extractNumber(argPacketType) << 48
        arguments = extractNumber(argArguments) << 56

        intVal = src + dst + payload + handler + packetType + arguments

    elif packetArgs[0] == "AMLongVector":
        assert (len(packetArgs) == 4 or len(packetArgs) == 6),\
            "Invalid number of arguments for AMLongVector"
        
        if ":" not in packetArgs[1]:
            if len(packetArgs) == 4:
                argDst = packetArgs[1]
                argDstSize = packetArgs[2]
                argToken = packetArgs[3]
            else:
                argSrc = packetArgs[1]
                argDst = packetArgs[2]
                argSrcSize = packetArgs[3]
                argDstSize = packetArgs[4]
                argToken = packetArgs[5]
        else:
            for arg in packetArgs[1:]:
                argList = arg.split(":")
                if argList[0] == "src":
                    argDst = argList[1]
                if argList[0] == "dst":
                    argDst = argList[1]
                elif argList[0] == "srcSize":
                    argSrcSize = argList[1]
                elif argList[0] == "dstSize":
                    argDstSize = argList[1]
                elif argList[0] == "token":
                    argToken = argList[1]
                else:
                    printError(1, "Invalid key for AMLongVector")
                    exit(1)

        if len(packetArgs) == 4:
            dst = extractNumber(argDst) << 4
            dstSize = extractNumber(argDstSize) << 20
            token = extractNumber(argToken) << 40
            intVal = dst + dstSize + token
        else:
            src = extractNumber(argSrc)
            dst = extractNumber(argDst) << 4
            srcSize = extractNumber(argSrcSize) << 8
            dstSize = extractNumber(argDstSize) << 20
            token = extractNumber(argToken) << 40
            intVal = src + dst + srcSize + dstSize + token

    elif packetArgs[0] == "AMLongStride":
        assert (len(packetArgs) == 4 or len(packetArgs) == 5), \
            "Invalid number of arguments for AMLongStride"

        if ":" not in packetArgs[1]:
            argStride = packetArgs[1]
            argBlockSize = packetArgs[2]
            argBlockNum = packetArgs[3]
            if len(packetArgs) == 5:
                argToken = packetArgs[4]
        else:
            for arg in packetArgs[1:]:
                argList = arg.split(":")
                if argList[0] == "stride":
                    argStride = argList[1]
                if argList[0] == "blockSize":
                    argBlockSize = argList[1]
                elif argList[0] == "blockNum":
                    argBlockNum = argList[1]
                elif argList[0] == "token":
                    argToken = argList[1]
                else:
                    printError(1, "Invalid key for AMLongStride")
                    exit(1)
        
        stride = extractNumber(argStride)
        blockSize = extractNumber(argBlockSize) << 16
        blockNum = extractNumber(argBlockNum) << 28
        if(len(packetArgs) == 5):
            token = extractNumber(argToken) << 40
            intVal += token
        intVal += stride + blockNum + blockSize

    elif packetArgs[0] == "dataMoverCommand":
        assert (len(packetArgs) == 8 or len(packetArgs) == 10),\
            "Invalid number of arguments for dataMoverCommand"

        if ":" not in packetArgs[1]:
            argBTT = packetArgs[1]
            argCommandType = packetArgs[2]
            argDSA = packetArgs[3]
            argEOF = packetArgs[4]
            argDRR = packetArgs[5]
            argAddr = packetArgs[6]
            argTag = packetArgs[7]
            if len(packetArgs) == 10:
                argUser = packetArgs[8]
                argCache = packetArgs[9]
        else:
            for arg in packetArgs[1:]:
                argList = arg.split(":")
                if argList[0] == "btt":
                    argBTT = argList[1]
                if argList[0] == "type":
                    argCommandType = argList[1]
                elif argList[0] == "dsa":
                    argDSA = argList[1]
                elif argList[0] == "eof":
                    argEOF = argList[1]
                elif argList[0] == "drr":
                    argDRR = argList[1]
                elif argList[0] == "addr":
                    argAddr = argList[1]
                elif argList[0] == "tag":
                    argTag = argList[1]
                elif argList[0] == "user":
                    argUser = argList[1]
                elif argList[0] == "cache":
                    argCache = argList[1]
                else:
                    printError(1, "Invalid key for dataMoverCommand")
                    exit(1)
        
        btt = extractNumber(argBTT)
        commandType = extractNumber(argCommandType) << 15
        dsa = extractNumber(argDSA) << 16
        eof = extractNumber(argEOF) << 22
        drr = extractNumber(argDRR) << 23
        addr = extractNumber(argAddr) << 24
        tag = extractNumber(argTag) << 56
        intVal = btt + commandType + dsa + eof + drr + addr + tag
        if len(packetArgs) == 10:
            xuser = extractNumber(argUser) << 64
            xcache = extractNumber(argCache) << 68
            intVal += xuser + xcache

    elif packetArgs[0] == "AMToken":
        assert(len(packetArgs) == 2), "Invalid number of arguments for AMToken"

        if ":" not in packetArgs[1]:
            argToken = packetArgs[1]
        else:
            for arg in packetArgs[1:]:
                argList = arg.split(":")
                if argList[0] == "token":
                    argToken = argList[1]
                else:
                    printError(1, "Invalid key for AMToken")
                    exit(1)

        token = extractNumber(argToken) << 40
        intVal = token
    else:
        printError(-1, "Unknown packet type: " + str(packetArgs[0]))
        exit(-1)

    return intVal

if __name__ == "__main__":

    for arg in sys.argv:
        if arg == "-h" or arg == "--help":
            print("Usage: python utilities.py [function] [args...]")
            print("Functions: ")
            print("   strToInt - <{type,arg0,arg1...argn}>, returns int")
            print("   extractNumber - <number string>, returns int")
            print("   evalMacro - <header, macro>, returns int")
            exit(1)

    if (len(sys.argv) > 1):
        if sys.argv[1] == "strToInt" and len(sys.argv) == 3:
            print(strToInt(sys.argv[2]))
        elif sys.argv[1] == "extractNumber" and len(sys.argv) == 3:
            print(extractNumber(sys.argv[2]))
        elif sys.argv[1] == "evalMacro" and len(sys.argv) == 4:
            print(evalMacro(sys.argv[2], sys.argv[3]))
        else:
            print("Unknown flags. Use -h or --help")
    else:
        print("Needs flags. Use -h or --help")