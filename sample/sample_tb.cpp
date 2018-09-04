#include <fstream>
#include <iostream>
#include <cstdlib>
#include "sample.hpp"
#include "testbench.hpp"

#define DAT_FILE "/GASCore/testbench/build/sample_c.dat" //relative to repo root

#define CALL_TB sample(axis_input, axis_output,ack, &state_out);

#define PRINT_AXIS std::cout << "Stream statuses:\n"; \
    std::cout << "  Input: " << axis_input.size() << "\n"; \
    std::cout << "  Output: " << axis_output.size() << "\n";

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

    axis_t axis_input;
    axis_t axis_output;
    uint_3_t state_out;

    uint_1_t ack; //output

    axis_word_t axis_word;

    uint_64_t readData;
    uint_1_t readLast;

    OPEN_FILE(testData)

    std::cout << "\n*** Starting SAMPLE_TB ***\n\n";

    std::string key, id;
    uint_64_t hexData;
    uint_1_t hexLast, callEnable;
    uint_11_t keep;
    bool valid = true;
    while(testData >> key >> hexData >> hexLast >> callEnable >> keep >> id){
        bool read = false;
        if(key.compare("axis_input") == 0){
            CHECK_DEBUG
            else{
                WRITE_WORD(axis_word, hexData, hexLast, axis_input)
            }
        }
        else if(key.compare("axis_output") == 0){
            CHECK_DEBUG
            else{
                read = true;
                READ_WORD(axis_word, readData, readLast, axis_output)
            }
        }
        else if(key.compare("END") == 0){
            if(!valid){
                std::cout << "Test " << std::hex << hexData << " failed\n";
            }
            else{
                std::cout << "Test " << std::hex << hexData << " successful\n";
            }
            valid = true;
        }
        else{
            std::cout << "Unknown key: " << key << "\n";
            return 1;
        }

        if(read){
            if(hexData != readData || hexLast != readLast){
                valid = false;
                std::cout << "Mismatch at id: " << id << "\n";
                std::cout << std::hex << "   Expected: " << hexData << " " << 
                    hexLast << "\n";
                std::cout << std::hex << "   Received: " << readData << " " << 
                    readLast << "\n";
            }
            else if(verbose > 0){
                std::cout << "Match:\n";
                std::cout << std::hex << "   Received: " << readData << " " << 
                    readLast << "id: " << id << "\n";
            }
        }
        else if(key.compare("END") != 0 && callEnable == 1){
            CALL_TB
        }
    }

    std::cout << "\n*** Finishing SAMPLE_TB ***\n";

    return 0;
    

}
