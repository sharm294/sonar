`timescale SONAR_TIMESCALE
////////////////////////////////////////////////////////////////////////////////
// Company: SONAR_COMPANY
// Engineer: SONAR_ENGINEER
//
// Create Date: SONAR_CURR_DATE
// Module Name: SONAR_MODULE_NAME
// Project Name: SONAR_PROJECT_NAME
// Target Devices: SONAR_TARGET_DEVICES
// Tool Versions: SONAR_TOOL_VERSIONS
// Description: SONAR_DESCRIPTION
//
// Dependencies: SONAR_DEPENDENCIES
//
////////////////////////////////////////////////////////////////////////////////

//filename for the input data file
string dataFileName = SONAR_DATA_FILE;

localparam MAX_DATA_SIZE = SONAR_MAX_DATA_SIZE; //max width of the data to be read/writtn
localparam MAX_VECTORS = SONAR_MAX_VECTORS; //number of test vectors
localparam MAX_PARALLEL = SONAR_MAX_PARALLEL;  //max number of parallel sections in any vector
localparam MAX_SEEK_SIZE = 64; //base 2 log of the max number to fseek
localparam MAX_ARG_NUM = SONAR_MAX_ARG_NUM;
localparam MAX_ARG_SIZE = $clog2(MAX_ARG_NUM) + 1;

SONAR_IMPORT_PACKAGES

//This module provides the stimulus for the DUT by reading the data file
module exerciser (
    SONAR_EXERCISER_PORTS
);

    logic [MAX_SEEK_SIZE-1:0] parallelSections [MAX_PARALLEL];

    logic [MAX_PARALLEL-1:0] testVectorEnd = 0;
    logic [MAX_PARALLEL-1:0] errorCheck = 0;
    logic [MAX_PARALLEL-1:0] threadSync = 0;
    logic [MAX_PARALLEL-1:0] threadSync_golden = 0;
    logic updateEnd = 0;
    logic fileReady = 0;

    task automatic evaluateData(
        input logic [MAX_DATA_SIZE-1:0] args [MAX_ARG_NUM],
        input string packetType_par,
        input string interfaceType_par,
        output logic done,
        output logic error
    );
        error = 0;
        done = 0;
        if (packetType_par == "wait") begin
            SONAR_IF_ELSE_WAIT
            else begin
                $display({"Unhandled case for wait type: ", interfaceType_par});
                error = 1'b1;
            end
        end
        else if (packetType_par == "signal") begin
            SONAR_IF_ELSE_SIGNAL
            else begin
                $display({"Unhandled case for signal type: ",
                    interfaceType_par});
                error = 1'b1;
            end
        end
        else if (packetType_par == "delay") begin
            if (interfaceType_par == "ns") begin
                #(args[0]);
            end
            else begin
                $display("Unhandled delay unit: %s", interfaceType_par);
                $display("\n*** Finishing RTL Simulation *** \n");
                $finish;
            end
        end
        else if (packetType_par == "display") begin
            $display("%s", interfaceType_par);
        end
        else if (packetType_par == "flag") begin
            if(interfaceType_par == "set") begin
                flags[args[0]] = 1;
            end
            else begin
                flags[args[0]] = 0;
            end
        end
        else if (packetType_par == "timestamp") begin
            SONAR_TIME_FORMAT
            if(interfaceType_par == "INIT") begin
                timeRef = $time;
            end
            else if(interfaceType_par == "PRINT") begin
                $display("%t", $time);
            end
            else begin
                $display("%s: %t", interfaceType_par, $time - timeRef);
            end
        end
        else if(packetType_par == "end") begin
            $display("Test vector %0d complete", args[0]);
            done = 1'b1;
        end
        SONAR_ELSE_IF_INTERFACE_IN
        SONAR_ELSE_IF_INTERFACE_OUT
        else begin
            $display({"Unhandled case: ", packetType_par, " " ,
                interfaceType_par});
            error = 1'b1;
            $display("\n*** Finishing RTL Simulation *** \n");
            $finish;
        end
    endtask

    //clock generation
    SONAR_INITIAL_CLOCK

    int vectorCount;
    time timeRef;
    logic [SONAR_FLAG_COUNT-1:0] flags = 0;

    SONAR_EXERCISER_PROLOGUE

    initial begin
        int status;
        string packetType;
        string interfaceType;

        logic [MAX_SEEK_SIZE-1:0] testVectors [MAX_VECTORS];

        int dataFile_0;
        int parallelSectionCount;

        SONAR_INITIAL_PROLOGUE

        dataFile_0 = $fopen(dataFileName, "r");
        status = $fscanf(dataFile_0, "%s %s %d\n", packetType, interfaceType,
            vectorCount);
        fileReady = 1;
        $display("\n*** Starting RTL Simulation *** \n");
        if (packetType == "TestVector" && interfaceType == "count") begin
            for(int i = 0; i < vectorCount; i++) begin
                status = $fscanf(dataFile_0, "%s %s %d\n", packetType,
                    interfaceType, testVectors[i]);
            end
            for(int i = 0; i < vectorCount; i++) begin
                status = $fseek(dataFile_0, testVectors[i], 0);
                status = $fscanf(dataFile_0, "%s %s %d\n", packetType,
                    interfaceType, parallelSectionCount);
                if (packetType == "ParallelSection" &&
                    interfaceType == "count") begin
                    for(int j = 0; j < parallelSectionCount; j++) begin
                        status = $fscanf(dataFile_0, "%s %s %d\n", packetType,
                            interfaceType,parallelSections[j]);
                    end
                    updateEnd = 1;
                    wait(|testVectorEnd == 1 && threadSync == threadSync_golden);
                    updateEnd = 0;
                    @(posedge SONAR_VECTOR_CLOCK)
                    for(int z = 0; z < MAX_PARALLEL; z++) begin
                        parallelSections[z] = 0;
                    end
                end
                else begin
                    $display("Bad data file - parallelsection header");
                    $display("\n*** Finishing RTL Simulation *** \n");
                    $finish;
                end
            end
            if (|errorCheck_latched) begin
                $display("Not all tests completed successfully. See above.");
            end else begin
                $display("All tests completed successfully!");
            end
            $display("\n*** Finishing RTL Simulation *** \n");
            $finish;
        end
        else begin
            $display("Bad data file - vector header");
            $display("\n*** Finishing RTL Simulation *** \n");
            $finish;
        end
    end

    logic [MAX_PARALLEL-1:0] errorCheck_latched = 0;
    always_ff @(posedge SONAR_VECTOR_CLOCK) begin
        errorCheck_latched <= errorCheck | errorCheck_latched;
    end

    generate;
        for(genvar gen_i = 0; gen_i < MAX_PARALLEL; gen_i++) begin
            initial begin
                int status_par;
                int dataFile;
                logic [MAX_DATA_SIZE-1:0] args [MAX_ARG_NUM];
                logic [MAX_ARG_SIZE-1:0] argCount;
                string packetType_par;
                string interfaceType_par;
                int packetCount;

                dataFile = $fopen(dataFileName, "r");
                wait(fileReady == 1);
                for(int w = 0; w < vectorCount; w++) begin
                    wait(updateEnd == 1'b1);
                    threadSync[gen_i] = 1'b0;
                    threadSync_golden[gen_i] = 1'b0;
                    if (parallelSections[gen_i] != 0) begin
                        threadSync_golden[gen_i] = 1'b1;
                        status_par = $fseek(dataFile, parallelSections[gen_i],
                            0);
                        status_par = $fscanf(dataFile, "%s %s %d",
                            packetType_par, interfaceType_par, packetCount);
                        for(int k = 0; k < packetCount; k++) begin
                            status_par = $fscanf(dataFile, "%s %s %d",
                                packetType_par, interfaceType_par, argCount);
                            for(int l = 0; l < argCount; l++) begin
                                status_par = $fscanf(dataFile, "%d", args[l]);
                            end
                            evaluateData(args, packetType_par,
                                interfaceType_par, testVectorEnd[gen_i], errorCheck[gen_i]);
                        end
                        threadSync[gen_i] = 1'b1;
                    end
                    wait(updateEnd == '0);
                    testVectorEnd = '0;
                end
            end
        end
    endgenerate

endmodule

module SONAR_MODULE_NAME_tb();

    SONAR_TB_SIGNAL_LIST

    SONAR_EXERCISER_INT

    SONAR_IP_INST

    //initialize DUT
    SONAR_DUT_INST

endmodule
