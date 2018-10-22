from include.utilities import printError
from include.utilities import extractNumber
import importlib

### strToInt ###
# This function converts a defined packed structure into an integer by 
# appropriately bitshifting and concatenating the different fields. New fields
# can be added as needed. To add custom packets that aren't broadly useful, 
# a similar function can be defined in the user_strToInt function in a 
# user_utilities.py file that is ignored on Git
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

    try:
        user_strToInt = importlib.import_module("user.user_strToInt")
    except ImportError:
        pass
    else:
        intVal = user_strToInt.strToInt(packet)
        if intVal is not None:
            return intVal

    # define common packet types: the following is included as an example
    # if packetArgs[0] == "AMHeader":
    #     assert (len(packetArgs) == 7),"Invalid number of arguments for AMHeader"
    #     if ":" not in packetArgs[1]:
    #         argSrc = packetArgs[1]
    #         argDst = packetArgs[2]
    #         argPayload = packetArgs[3]
    #         argHandler = packetArgs[4]
    #         argPacketType = packetArgs[5]
    #         argArguments = packetArgs[6]
    #     else:
    #         for arg in packetArgs[1:]:
    #             argList = arg.split(":")
    #             if argList[0] == "src":
    #                 argSrc = argList[1]
    #             elif argList[0] == "dst":
    #                 argDst = argList[1]
    #             elif argList[0] == "payload":
    #                 argPayload = argList[1]
    #             elif argList[0] == "handler":
    #                 argHandler = argList[1]
    #             elif argList[0] == "type":
    #                 argPacketType = argList[1]
    #             elif argList[0] == "args":
    #                 argArguments = argList[1]
    #             else:
    #                 printError(1, "Invalid key for AMHeader")
    #                 exit(1)
    #     src = extractNumber(argSrc)
    #     dst = extractNumber(argDst) << 16
    #     payload = extractNumber(argPayload) << 32
    #     handler = extractNumber(argHandler) << 44
    #     packetType = extractNumber(argPacketType) << 48
    #     arguments = extractNumber(argArguments) << 56

    #     intVal = src + dst + payload + handler + packetType + arguments
    # else:

    printError(1, "Unknown packet type: " + packetArgs[0])
    exit(1)
