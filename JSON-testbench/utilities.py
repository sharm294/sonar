import sys

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
        src = extractNumber(packetArgs[1])
        dst = extractNumber(packetArgs[2]) << 16
        payload = extractNumber(packetArgs[3]) << 32
        handler = extractNumber(packetArgs[4]) << 44
        packetType = extractNumber(packetArgs[5]) << 48
        arguments = extractNumber(packetArgs[6]) << 56
        intVal = src + dst + payload + handler + packetType + arguments

    elif packetArgs[0] == "AMLongVector":
        if len(packetArgs) == 4:
            dst = extractNumber(packetArgs[1]) << 4
            dstSize = extractNumber(packetArgs[2]) << 20
            token = extractNumber(packetArgs[3]) << 40
            intVal = dst + dstSize + token
        elif len(packetArgs) == 6:
            src = extractNumber(packetArgs[1])
            dst = extractNumber(packetArgs[2]) << 4
            srcSize = extractNumber(packetArgs[3]) << 8
            dstSize = extractNumber(packetArgs[4]) << 20
            token = extractNumber(packetArgs[5]) << 40
            intVal = src + dst + srcSize + dstSize + token
        else:
            print("Invalid number of arguments for AMLongVector")
            exit(-1)

    elif packetArgs[0] == "AMLongStride":
        assert (len(packetArgs) == 5),"Invalid number of arguments for AMLongStride"
        stride = extractNumber(packetArgs[1])
        blockSize = extractNumber(packetArgs[2]) << 16
        blockNum = extractNumber(packetArgs[3]) << 28
        token = extractNumber(packetArgs[4]) << 40
        intVal = stride + blockNum + blockSize + token

    elif packetArgs[0] == "AMHeaderOld":
        assert (len(packetArgs) == 4),"Invalid number of arguments for AMHeaderOld"
        src = extractNumber(packetArgs[1])
        dst = extractNumber(packetArgs[2]) << 8
        words = extractNumber(packetArgs[3]) << 16
        intVal = src + dst + words

    elif packetArgs[0] == "dataMoverCommand":
        assert (len(packetArgs) == 10 or len(packetArgs) == 8),\
            "Invalid number of arguments for dataMoverCommand"
        btt = extractNumber(packetArgs[1])
        commandType = extractNumber(packetArgs[2]) << 15
        dsa = extractNumber(packetArgs[3]) << 16
        eof = extractNumber(packetArgs[4]) << 22
        drr = extractNumber(packetArgs[5]) << 23
        addr = extractNumber(packetArgs[6]) << 24
        tag = extractNumber(packetArgs[7]) << 56
        intVal = btt + commandType + dsa + eof + drr + addr + tag
        if len(packetArgs) == 10:
            xuser = extractNumber(packetArgs[8]) << 64
            xcache = extractNumber(packetArgs[9]) << 68
            intVal += xuser + xcache

    elif packetArgs[0] == "AMToken":
        assert(len(packetArgs) == 2), "Invalid number of arguments for AMToken"
        token = extractNumber(packetArgs[1]) << 40
        intVal = token
    else:
        print("Unknown packet type: " + str(packetArgs[0]))
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