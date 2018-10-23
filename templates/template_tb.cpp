#include <stdio.h>
#include <iostream>
#include <cstdlib>
#include #HEADER_FILE#

#define DAT_FILE #DATA_FILE#

int main(int argc, char* argv[]){
    int i;
    bool printState = false;
    bool printMatches = false;
    bool printInterfaces = false;
    bool readInterfaces = false;
    for(i = 1; i < argc; i++){
        if (std::string(argv[i]).compare("--printStates") == 0){
            printState = true;
        } else if(std::string(argv[i]).compare("--printMatches") == 0){
            printMatches = true;
        } else if(std::string(argv[i]).compare("--printInterfaces") == 0){
            printInterfaces = true;
        } else if(std::string(argv[i]).compare("--readInterfaces") == 0){
            readInterfaces = true;
        } else {
            std::cout << "Not enough or invalid arguments, please try again.\n";
            return 2;
        }
    }

    DECLARE_VARIABLES

    FILE * dataFile = fopen(DAT_FILE, "r");

    std::cout << "\n*** Starting #FUNCTION#_TB ***\n\n";

    char interfaceType [#MAX_STRING_SIZE#];
    char cStreamType [#MAX_STRING_SIZE#];
    char id [#MAX_STRING_SIZE#];
    int argCount;
    ap_uint<#MAX_DATA_SIZE#> readArgs [#MAX_ARG_NUM#];
    ap_uint<#MAX_DATA_SIZE#> args [#MAX_ARG_NUM#];
    bool valid = true;
    int callTB = 0;
    #ifdef DEBUG
    int dbg_currentState;
    #endif
    while(1){
        bool read = false;

        fscanf(dataFile, "%s %s %s %d %d", interfaceType, id, cStreamType, &argCount, &callTB);
        for(int l = 0; l < argCount; l++){
            fscanf(dataFile, "%ld", args[l]); //C++ can only support 64bit args
        }

        #ELSE_IF_SIGNAL#
        #ELSE_IF_INTERFACE_IN#
        #ELSE_IF_INTERFACE_OUT#
        else if((!strcmp(interfaceType,"timestamp")) || (!strcmp(interfaceType,"display"))){
            if(strcmp(id,"INIT")){
                std::cout << id << "\n";
            }
        }
        else if(!strcmp(interfaceType,"end")){
            if(!valid){
                std::cout << "Test " << args[0] << " failed\n";
            }
            else{
                std::cout << "Test " << args[0] << " successful\n";
            }
            valid = true;
        }
        else if(!strcmp(interfaceType,"finish")){
            break;
        }
        else{
            std::cout << "Unknown interfaceType: " << interfaceType << "\n";
            return 1;
        }

        if(read){
            VERIFY(cStreamType)
            else if (printMatches){
                std::cout << "Match at id: " << id << "\n";
                std::cout << std::hex << "   Received: " << readArgs[0] << " " << 
                    readArgs[1] << "\n";
            }
        }
        
        if(callTB > 0){
            for(int l = 0; l < callTB; l++){
                CALL_TB
                #if defined(DEBUG) && defined(FSM_EXISTS)
                if (printState){
                    std::cout << "Current State is " + stateParse(dbg_currentState) << "\n";
                }
                #endif
            }
        }

        if (printInterfaces){
            PRINT_INTERFACES
        }

    }

    if (readInterfaces){
        READ_INTERFACES
    }

    std::cout << "\n*** Finishing #FUNCTION#_TB ***\n";

    fclose(dataFile);

    return 0;
    
}
