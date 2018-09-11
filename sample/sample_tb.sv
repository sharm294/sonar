`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 08/22/2018 09:57:31 PM
// Design Name: 
// Module Name: sample_tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

//defines the axis interfaces
`include "axis_interface.sv"

//filename for the input data file
string dataFileName = "sample_sv.dat";

localparam CLOCK_PERIOD = 20ns;
localparam MAX_DATA_SIZE = 64; //max width of the data to be read/writtn
localparam MAX_VECTORS = 5; //number of test vectors
localparam MAX_PARALLEL = 3;  //max number of parallel sections in any vector
localparam MAX_SEEK_SIZE = 64; //base 2 log of the max number to fseek
localparam MAX_KEEP_SIZE = 4; //max width of the keep field in axis

//This module provides the stimulus for the DUT by reading the data file
module exerciser (
    output logic clock,
    output logic rst_n,

    input ack,
    axi_stream.axis_m_mp AXIS_M,
    axi_stream.axis_s_mp AXIS_S
);

    logic [MAX_SEEK_SIZE-1:0] parallelSections [MAX_PARALLEL];

    logic [MAX_PARALLEL-1:0] testVectorEnd = 0;
    logic updateEnd = 0;

    /***************************************************************************
    * EDIT THIS TASK AS NEEDED
    ***************************************************************************/
    task evaluateData(
        input logic [MAX_DATA_SIZE-1:0] tdata,
        input logic tlast,
        input logic [MAX_KEEP_SIZE-1:0] tkeep,
        input string packetType_par,
        input string interfaceType_par,
        output logic done
    );
        
        if (packetType_par == "wait") begin
            if(interfaceType_par == "ack") begin
                wait(ack == tdata);
            end
            else begin
                $display({"Unhandled case for wait type: ", interfaceType_par});
            end
        end
        else if (packetType_par == "signal") begin
            if(interfaceType_par == "rst_n") begin
                rst_n = tdata;
            end
            else begin
                $display({"Unhandled case for signal type: ", 
                    interfaceType_par});
            end
        end
        else if (packetType_par == "delay") begin
            if(interfaceType_par == "ns") begin
                #(tdata);
            end
            else begin
                $display({"Unhandled case for delay type: ", 
                    interfaceType_par});
            end
        end
        else if(packetType_par == "end") begin
            done = 1'b1;
        end
        else if (interfaceType_par == "axis_input") begin
            AXIS_M.tvalid = 1'b1;
            AXIS_M.tdata = tdata;
            AXIS_M.tlast = tlast;
            @(posedge clock iff AXIS_M.tready)
            @(posedge clock)
            AXIS_M.tvalid = '0;
        end
        else if (interfaceType_par == "axis_output") begin
            @(posedge clock iff AXIS_S.tready && AXIS_S.tvalid)
            assert(AXIS_S.tdata == tdata);
            assert(AXIS_S.tlast == tlast);
        end
        
        else begin
            $display({"Unhandled case: ", packetType_par, " " , 
                interfaceType_par});
            $finish;
        end
    endtask

    /***************************************************************************
    * DO NOT EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
    ***************************************************************************/

    //clock generation
    initial begin
        clock = 0;
        forever begin
            #(CLOCK_PERIOD/2) clock <= ~clock;
        end
    end
    
    int vectorCount;

    initial begin
        int status;
        string packetType;
        string interfaceType;

        logic [MAX_SEEK_SIZE-1:0] testVectors [MAX_VECTORS];

        int dataFile_0;
        int parallelSectionCount;

        AXIS_M.tvalid = 1'b0;
        AXIS_M.tdata = 1'b0;
        AXIS_M.tlast = 1'b0;
        AXIS_S.tready = 1'b1;

        dataFile_0 = $fopen(dataFileName, "r");
        status = $fscanf(dataFile_0, "%s %s %d\n", packetType, interfaceType, 
            vectorCount);
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
                    wait(|testVectorEnd == 1);
                    updateEnd = 0;
                    @(posedge clock)
                    for(int z = 0; z < MAX_PARALLEL; z++) begin
                        parallelSections[z] = 0;
                    end
                end
                else begin
                    $display("Bad data file - parallelsection header");
                    $finish;
                end
            end
            $display("All tests completed!");
        end
        else begin
            $display("Bad data file - vector header");
            $finish;
        end
    end    

    generate;
        for(genvar gen_i = 0; gen_i < MAX_PARALLEL; gen_i++) begin
            initial begin
                int status_par;
                int dataFile; 
                logic [MAX_DATA_SIZE-1:0] tdata;
                logic tlast;
                logic [MAX_KEEP_SIZE-1:0] tkeep; 
                string packetType_par; 
                string interfaceType_par; 
                int packetCount;
                
                dataFile = $fopen(dataFileName, "r");
                for(int w = 0; w < vectorCount; w++) begin
                    wait(updateEnd == 1'b1);
                    if (parallelSections[gen_i] != 0) begin
                        status_par = $fseek(dataFile, parallelSections[gen_i], 
                            0);
                        status_par = $fscanf(dataFile, "%s %s %d\n", 
                            packetType_par, interfaceType_par, packetCount);
                        for(int k = 0; k < packetCount; k++) begin
                            status_par = $fscanf(dataFile, "%s %s %d %d %d\n", 
                                packetType_par, interfaceType_par , tdata, 
                                tlast, tkeep);

                            evaluateData(tdata, tlast, tkeep, packetType_par,
                                interfaceType_par, testVectorEnd[gen_i]);
                        end
                    end
                    wait(updateEnd == '0);
                    testVectorEnd = '0;                    
                end
            end
        end
    endgenerate
   
endmodule

module sample_tb();

    logic clock;
    logic rst_n;

    logic ack;
    logic [2:0] state_out;

    logic [MAX_DATA_SIZE-1:0] input_tdata;
    logic input_tlast;
    logic input_tready;
    logic input_tvalid;

    logic [MAX_DATA_SIZE-1:0] output_tdata;
    logic output_tlast;
    logic output_tready;
    logic output_tvalid;

    //initialize interfaces
    axi_stream master(
        .aclk(clock)
    );
    
    axi_stream slave(
        .aclk(clock)
    );

    axis_m master_m(
        .AXIS_M(master),
        .tdata(input_tdata),
        .tvalid(input_tvalid),
        .tlast(input_tlast),
        .tready(input_tready)
    );

    axis_s slave_s(
        .AXIS_S(slave),
        .tdata(output_tdata),
        .tvalid(output_tvalid),
        .tlast(output_tlast),
        .tready(output_tready)
    );

    exerciser exerciser_i(
        .clock(clock),
        .ack(ack),
        .rst_n(rst_n),
        .AXIS_M(master),
        .AXIS_S(slave)
    );

    always_comb begin
        master_m.write();
        slave_s.read();
    end

    //initialize DUT
    sample sample_i(
        .ack_V(ack),
        .ap_clk(clock),
        .ap_rst_n(rst_n),
        .axis_input_TDATA(input_tdata),
        .axis_input_TLAST(input_tlast),
        .axis_input_TREADY(input_tready),
        .axis_input_TVALID(input_tvalid),
        .axis_output_TDATA(output_tdata),
        .axis_output_TLAST(output_tlast),
        .axis_output_TREADY(output_tready),
        .axis_output_TVALID(output_tvalid),
        .state_out_V(state_out)
    );

endmodule