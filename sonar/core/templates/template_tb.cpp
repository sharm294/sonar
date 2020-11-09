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
#include <assert.h>
#include <string>

SONAR_HEADER_FILE

#define DAT_FILE SONAR_DATA_FILE
#define SONAR_MAX_STRING_SIZE 255

int main(int argc, char* argv[]) {
  // int i;
  // bool printMatches = false;
  // bool printInterfaces = false;
  // bool readInterfaces = false;
  // for (i = 1; i < argc; i++) {
  //   if (std::string(argv[i]).compare("--printMatches") == 0) {
  //     printMatches = true;
  //   } else if (std::string(argv[i]).compare("--printInterfaces") == 0) {
  //     printInterfaces = true;
  //   } else if (std::string(argv[i]).compare("--readInterfaces") == 0) {
  //     readInterfaces = true;
  //   } else {
  //     std::cout << "Not enough or invalid arguments, please try again.\n";
  //     return 2;
  //   }
  // }

  SONAR_TB_SIGNAL_LIST

  FILE* dataFile = fopen(DAT_FILE, "r");
  if (dataFile == NULL) {
    perror("Failed: ");
    return 1;
  }

  std::cout << "\n*** Starting testbench ***\n\n";

  char interfaceType[SONAR_MAX_STRING_SIZE];
  char cStreamType[SONAR_MAX_STRING_SIZE];
  char id[SONAR_MAX_STRING_SIZE];
  int argCount;
  // ap_uint<SONAR_MAX_DATA_SIZE> readArgs[SONAR_MAX_ARG_NUM];
  long long args[SONAR_MAX_ARG_NUM];
  // bool valid = true;
  // int callTB = 0;
#ifdef DEBUG
  int dbg_currentState;
#endif
  while (1) {
    fscanf(dataFile, "%s %s %s %d", interfaceType, id, cStreamType,
           &argCount);
    for (int l = 0; l < argCount; l++) {
      fscanf(dataFile, "%lld", &(args[l]));  // C++ can only support 64bit args
    }

    SONAR_IF_ELSE_SIGNAL
    SONAR_ELSE_IF_INTERFACE_IN
    SONAR_ELSE_IF_INTERFACE_OUT
    else if ((!strcmp(interfaceType, "timestamp")) ||
             (!strcmp(interfaceType, "display"))) {
      if (strcmp(id, "INIT")) {
        std::cout << id << "\n";
      }
    }
    else if (!strcmp(interfaceType, "call_dut")) {
      for (int l = 0; l < args[0]; l++) {
        CALL_TB
      }
    }
    else if (!strcmp(interfaceType, "end")) {
      std::cout << "Test " << args[0] << " successful\n";
    }
    else if (!strcmp(interfaceType, "finish")) {
      break;
    }
    else {
      std::cout << "Unknown interfaceType: " << interfaceType << "\n";
      return 1;
    }
  }

  std::cout << "\n*** Finishing testbench ***\n";

  fclose(dataFile);

  return 0;
}
