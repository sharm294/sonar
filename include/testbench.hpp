#ifndef TESTBENCH_H_
#define TESTBENCH_H_

#ifdef DEBUG
#define CHECK_DEBUG \
    if(keep > 255){ \
        switch(hexData){ \
            case 0:{ \
                PRINT_AXIS \
                break; \
            } \
            case 1:{ \
                std::cout << "Current State is " << stateParse(dbg_currentState) << "\n"; \
                break; \
            } \
            case 2:{ \
                \
                break; \
            } \
            default:{ \
                std::cout << "Error: Unknown debug code " << hexData << "\n"; \
                break; \
            } \
        } \
    }
#else
#define CHECK_DEBUG if(keep > 255){}
#endif

#define OPEN_FILE(fileName) \
    char const* tmp_repo_path = std::getenv("SHOAL_PATH"); \
    if(tmp_repo_path == NULL){ \
        std::cout << "SHOAL_PATH not set in environment\n"; \
        return -1; \
    } \
    std::string repo_path(tmp_repo_path); \
    std::ifstream fileName(repo_path.append(DAT_FILE).c_str()); \
    if (!fileName){ \
        std::cout << "Unable to open test data file\n"; \
        return -1; \
    }

#endif
