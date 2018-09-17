#include <stdio.h>
#include <iostream>
#include <cstdlib>
#include #HEADER_FILE#

#define DAT_FILE #DATA_FILE#

int main(int argc, char* argv[]){
    int i;
    int verbose = 0;
    for(i = 1; i < argc; i++){
        if (std::string(argv[i]).compare("-v") == 0) {
            verbose++;
        } else {
            std::cout << "Not enough or invalid arguments, please try again.\n";
            return 2;
        }
    }

    DECLARE_VARIABLES

    FILE * dataFile = fopen(DAT_FILE, "r");

    std::cout << "\n*** Starting #FUNCTION#_TB ***\n\n";

    char interfaceType [#MAX_STRING_SIZE#];
    char id [#MAX_STRING_SIZE#];
    int argCount;
    ap_uint<#MAX_DATA_SIZE#> readArgs [#MAX_ARG_NUM#];
    ap_uint<#MAX_DATA_SIZE#> args [#MAX_ARG_NUM#];
    bool valid = true;
    int callTB = 0;
    while(1){
        bool read = false;

        fscanf(dataFile, "%s %s %d %d", interfaceType, id, &argCount, &callTB);
        for(int l = 0; l < argCount; l++){
            fscanf(dataFile, "%d", args[l]);
        }

        #ELSE_IF_INTERFACE_IN#
        #ELSE_IF_INTERFACE_OUT#
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
            VERIFY
        }
        
        if(callTB > 0){
            for(int l = 0; l < callTB; l++){
                CALL_TB
            }
        }
    }

    std::cout << "\n*** Finishing #FUNCTION#_TB ***\n";

    fclose(dataFile);

    return 0;
    
}
