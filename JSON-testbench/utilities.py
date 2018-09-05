import sys
import os

### GetFilePath ###
# This function checks if a file exists and returns the absolute path to it
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
# Return: a string containing the absolute path of the filename if found. None 
#   otherwise.
def getFilePath(mode, modeArg, filepath):
    if mode == "env":
        if modeArg is None:
            printError(1, "getFilePath - the mode argument must not be None for env")
            return None
        else:
            path = getEnvironmentVar(modeArg)
            if path is None:
                printError(1, "getFilePath - environment variable not found: " + modeArg)
                return None
    elif mode == "path":
        if modeArg is None:
            printError(1, "getFilePath - the mode argument must not be None for path")
            return None
        path = modeArg
    elif mode == "absolute":
        path = ""
    else:
        printError(1, "getFilePath - unknown mode option: " + mode)
        return None

    testFileName = path + filepath

    if not os.path.isfile(testFileName):
        message = "getFilePath - file does not exist: " + filePath
        printError(2, message)
        return None
    else:
        return testFileName

### trimFinalLine ###
# This function removes the final line from a file
#
# Arguments:
#   openFile: an open file object to trim
#
# Return: N/A
def trimFinalLine(openFile):
    openFile.seek(0, os.SEEK_END) #move to end of file
    pos = openFile.tell()
    while pos > 0 and openFile.read(1) != "\n": #traverse back until \n
        pos -= 1
        openFile.seek(pos, os.SEEK_SET)

    if pos > 0: #if we're not at the start, delete chars ahead
        openFile.seek(pos, os.SEEK_SET)
        openFile.truncate()

### getEnvironmentVar ###
# This function evaluates an environment variable and returns its value
#
# Arguments:
#   envVar: environment variable to evaluate (string)
#
# Return: environment variable value (string) or None (if not found)
def getEnvironmentVar(envVar):
    variable = os.environ.get(envVar)
    if variable is None:
        printError(1, "getEnvironmentVar - environment variable not found: " + variable)
        return None
    else:
        return variable

### stripFileName ###
# This function strips the unnecessary parts of the absolute path of a file to 
# improve legibility
#
# Arguments:
#   mode: must be one of "env" or "path"
#       - "env" considers modeArg as an environment variable and strips it
#       - "path" considers modeArg as a string and strips it
#   modeArg: a string argument used in conjunction with mode
#   filepath: a string argument for the filepath to strip
#
# Return: the stripped filepath (string) or None (if error)
#TODO delete if no longer needed
# def stripFileName(mode, modeArg, filename):  
#     if mode == "env":
#         if modeArg is None:
#             printError(1, "stripFileName - the mode argument must not be None for env")
#             return None
#         else:
#             stripHeader = getEnvironmentVar(modeArg)
#             if stripHeader is None:
#                 printError(1, "stripFileName - environment variable not found: " + modeArg)
#                 return None
#     elif mode == "path":
#         if modeArg is None:
#             printError(1, "stripFileName - the mode argument must not be None for path")
#             return None
#         stripHeader = modeArg
#     else:
#         printError(1, "stripFileName - unknown mode option: " + mode)
#         return None

#     localName = filename.replace(stripHeader, '')
#     return localName

def printWarning(message):
    print("*** Warning *** : " + message)

def printError(errorCode, message):
    print("*** Fatal Error *** Code " + str(errorCode) + ": " + message)

### extractNumber ###
# This function converts a(n encoded) string into an integer.
#
# Arguments:
#   numberStr: the string to convert
#
# Return: the integer. May raise an error if an unhandled case occurs
#TODO handle exceptions for graceful exit
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

### strToInt ###
# This function converts a defined packed structure into an integer by 
# appropriately bitshifting and concatenating the different fields. New fields
# can be added as needed.
#
# Arguments:
#   packet: the string to convert. Must be in the format:
#       - {type,arg0,arg1,...,argn} for implicit conversion
#       - {type,name0:arg0,name1:arg1...namen:argn} for named conversion
#
# Return: the evaluated integer. May raise an error if an unhandled case occurs
#TODO enforce data size checking for arguments
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
            print("   strToInt {type,arg0,arg1...argn}, returns int")
            print("   extractNumber number string, returns int")
            exit(1)

    if (len(sys.argv) > 1):
        if sys.argv[1] == "strToInt" and len(sys.argv) == 3:
            print(strToInt(sys.argv[2]))
        elif sys.argv[1] == "extractNumber" and len(sys.argv) == 3:
            print(extractNumber(sys.argv[2]))
        else:
            print("Unknown flags. Use -h or --help")
    else:
        print("Needs flags. Use -h or --help")