interface axi_stream #(
    parameter DATA_WIDTH = 64
)(
    input logic aclk
);

    logic [DATA_WIDTH-1:0] tdata;
    logic tvalid;
    logic tready;
    logic tlast;   

    // // clocking block for AXI Stream master
    // clocking cb_axis_m @(posedge aclk);
    //   default input #1step output #3ns;
    //   output tdata;
    //   output tvalid;
    //   output tlast;
    //   input tready;
    // endclocking

    // // clocking block for AXI Stream slave
    // clocking cb_axis_s @(posedge aclk);
    //   default input #1step output #2ns;
    //   input tdata;
    //   input tvalid;
    //   input tlast;
    //   output tready;
    // endclocking     

    // // AXI stream master modport - for testbench only
    // modport tb_axis_m_mp(
    //     clocking cb_axis_m,
    //     output tdata,
    //     output tvalid,
    //     output tlast,
    //     input tready
    // );

    // // AXI stream slave modport - for testbench only
    // modport tb_axis_s_mp(
    //     clocking cb_axis_s,
    //     input tdata,
    //     input tvalid,
    //     input tlast,
    //     output tready
    // );   
    
    // AXI stream master modport - for synthesis
    modport axis_m_mp(
        output tdata,
        output tvalid,
        output tlast,
        input tready
    );
    
    // AXI stream slave modport - for synthesis
    modport axis_s_mp(
        input tdata,
        input tvalid,
        input tlast,
        output tready
    );
    
endinterface: axi_stream

interface axis_s #(
    parameter DATA_WIDTH = 64
)(
    axi_stream.axis_s_mp AXIS_S,
    input [DATA_WIDTH-1:0] tdata,
    input tvalid,
    input tlast,
    output logic tready
);

    function void read;
        assign AXIS_S.tdata = tdata;
        assign AXIS_S.tvalid = tvalid;
        assign AXIS_S.tlast = tlast;
        assign tready = AXIS_S.tready;
    endfunction
endinterface: axis_s

interface axis_m #(
    parameter DATA_WIDTH = 64
)(
    axi_stream.axis_m_mp AXIS_M,
    output logic [DATA_WIDTH-1:0] tdata,
    output logic tvalid,
    output logic tlast,
    input tready
);

    function void write;
        assign tdata = AXIS_M.tdata;
        assign tvalid = AXIS_M.tvalid;
        assign tlast = AXIS_M.tlast;
        assign AXIS_M.tready = tready;
    endfunction
endinterface: axis_m