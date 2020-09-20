import sys
import os
import importlib

sonar_types = [
    "delay",
    "wait",
    "signal",
    "end",
    "timestamp",
    "display",
    "flag",
    "call_dut",
]


# This function attempts to import an interface definition
def getInterface(interfaceName):
    # first check user's directory
    # try:
    #     interface = importlib.import_module("user.interfaces." + interfaceName)
    # except ImportError:
    #     pass
    # else:
    #     return interface

    # then check Sonar directory
    try:
        interface = importlib.import_module(
            "sonar.core.include.interfaces." + interfaceName
        )
    except ImportError:
        printError(1, "Unknown interface type: " + interfaceName)
        return None
    else:
        return interface


# This function extracts the indentation level of a line
# Return: a string containing the leading whitespace
def getIndentation(textStr):
    try:
        indent = textStr[0][: len(textStr[0]) - len(textStr[0].lstrip())]
    except IndexError:
        printError(1, "String " + str(textStr) + " not found")
        exit(1)
    else:
        return indent


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
                printError(
                    1, "getFilePath - environment variable not found: " + modeArg
                )
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
        message = "testFileName - file does not exist: " + testFileName
        printError(2, message)
        return None
    else:
        return testFileName


# This function removes the final line from a file
#
# Arguments:
#   openFile: an open file object to trim
#
# Return: N/A
def trimFinalLine(openFile):
    openFile.seek(0, os.SEEK_END)  # move to end of file
    pos = openFile.tell()
    while pos > 0 and openFile.read(1) != "\n":  # traverse back until \n
        pos -= 1
        openFile.seek(pos, os.SEEK_SET)

    if pos > 0:  # if we're not at the start, delete chars ahead
        openFile.seek(pos, os.SEEK_SET)
        openFile.truncate()


# This function evaluates an environment variable and returns its value
#
# Arguments:
#   envVar: environment variable to evaluate (string)
#
# Return: environment variable value (string) or None (if not found)
def getEnvironmentVar(envVar):
    variable = os.getenv(envVar)
    if variable is None:
        printError(1, "getEnvironmentVar - environment variable not found: " + variable)
        return None
    else:
        return variable


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
def stripFileName(mode, modeArg, filename):
    if mode == "env":
        if modeArg is None:
            printError(1, "stripFileName - the mode argument must not be None for env")
            return None
        else:
            stripHeader = getEnvironmentVar(modeArg)
            if stripHeader is None:
                printError(
                    1, "stripFileName - environment variable not found: " + modeArg
                )
                return None
    elif mode == "path":
        if modeArg is None:
            printError(1, "stripFileName - the mode argument must not be None for path")
            return None
        stripHeader = modeArg
    else:
        printError(1, "stripFileName - unknown mode option: " + mode)
        return None

    localName = filename.replace(stripHeader, "")
    return localName


def printWarning(message):
    print("*** Warning *** : " + message)


def printError(errorCode, message):
    print("*** Fatal Error *** Code " + str(errorCode) + ": " + message)


# This function converts a(n encoded) string into an integer.
#
# Arguments:
#   numberStr: the string to convert
#
# Return: the integer. May raise an error if an unhandled case occurs
# TODO handle exceptions for graceful exit
def extractNumber(numberStr):
    if not isinstance(numberStr, (int)):
        if numberStr[:2] == "0x":
            number = int(numberStr, 16)
        elif numberStr[:2] == "0b":
            number = int(numberStr, 2)
        else:
            number = int(numberStr, 10)

        return number
    else:
        return int(numberStr, 10)


if __name__ == "__main__":

    for arg in sys.argv:
        if arg == "-h" or arg == "--help":
            print("Usage: python utilities.py [function] [args...]")
            print("Functions: ")
            print("   strToInt {type,arg0,arg1...argn}, returns int")
            print("   extractNumber number string, returns int")
            exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] == "strToInt" and len(sys.argv) == 3:
            # print(strToInt(sys.argv[2]))
            print("deprecated")
        elif sys.argv[1] == "extractNumber" and len(sys.argv) == 3:
            print(extractNumber(sys.argv[2]))
        else:
            print("Unknown flags. Use -h or --help")
    else:
        print("Needs flags. Use -h or --help")
