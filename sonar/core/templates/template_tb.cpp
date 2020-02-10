/*******************************************************************************

The MIT License (MIT)

Copyright (c) 2020 Varun Sharma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*******************************************************************************/

#include <stdio.h>
#include <cstdlib>
#include <iostream>
#include SONAR_HEADER_FILE

#define DAT_FILE SONAR_DATA_FILE

int main(int argc, char* argv[]) {
  int i;
  bool printState = false;
  bool printMatches = false;
  bool printInterfaces = false;
  bool readInterfaces = false;
  for (i = 1; i < argc; i++) {
    if (std::string(argv[i]).compare("--printStates") == 0) {
      printState = true;
    } else if (std::string(argv[i]).compare("--printMatches") == 0) {
      printMatches = true;
    } else if (std::string(argv[i]).compare("--printInterfaces") == 0) {
      printInterfaces = true;
    } else if (std::string(argv[i]).compare("--readInterfaces") == 0) {
      readInterfaces = true;
    } else {
      std::cout << "Not enough or invalid arguments, please try again.\n";
      return 2;
    }
  }

  DECLARE_VARIABLES

  FILE* dataFile = fopen(DAT_FILE, "r");

  std::cout << "\n*** Starting SONAR_FUNCTION_TB ***\n\n";

  char interfaceType[SONAR_MAX_STRING_SIZE];
  char cStreamType[SONAR_MAX_STRING_SIZE];
  char id[SONAR_MAX_STRING_SIZE];
  int argCount;
  ap_uint<SONAR_MAX_DATA_SIZE> readArgs[SONAR_MAX_ARG_NUM];
  ap_uint<SONAR_MAX_DATA_SIZE> args[SONAR_MAX_ARG_NUM];
  bool valid = true;
  int callTB = 0;
#ifdef DEBUG
  int dbg_currentState;
#endif
  while (1) {
    bool read = false;

    fscanf(dataFile, "%s %s %s %d %d", interfaceType, id, cStreamType,
           &argCount, &callTB);
    for (int l = 0; l < argCount; l++) {
      fscanf(dataFile, "%ld", args[l]);  // C++ can only support 64bit args
    }

    SONAR_ELSE_IF_SIGNAL
    SONAR_ELSE_IF_INTERFACE_IN
    SONAR_ELSE_IF_INTERFACE_OUT
    else if ((!strcmp(interfaceType, "timestamp")) ||
             (!strcmp(interfaceType, "display"))) {
      if (strcmp(id, "INIT")) {
        std::cout << id << "\n";
      }
    }
    else if (!strcmp(interfaceType, "end")) {
      if (!valid) {
        std::cout << "Test " << args[0] << " failed\n";
      } else {
        std::cout << "Test " << args[0] << " successful\n";
      }
      valid = true;
    }
    else if (!strcmp(interfaceType, "finish")) {
      break;
    }
    else {
      std::cout << "Unknown interfaceType: " << interfaceType << "\n";
      return 1;
    }

    if (read) {
      VERIFY(cStreamType)
      else if (printMatches) {
        std::cout << "Match at id: " << id << "\n";
        std::cout << std::hex << "   Received: " << readArgs[0] << " "
                  << readArgs[1] << "\n";
      }
    }

    if (callTB > 0) {
      for (int l = 0; l < callTB; l++) {
        CALL_TB
#if defined(DEBUG) && defined(FSM_EXISTS)
        if (printState) {
          std::cout << "Current State is " + stateParse(dbg_currentState)
                    << "\n";
        }
#endif
      }
    }

    if (printInterfaces) {
      PRINT_INTERFACES
    }
  }

  if (readInterfaces) {
    READ_INTERFACES
  }

  std::cout << "\n*** Finishing SONAR_FUNCTION_TB ***\n";

  fclose(dataFile);

  return 0;
}
