interface axis #(
    parameter DATA_WIDTH = 16
) (input logic aclk);

    logic [DATA_WIDTH-1:0] tdata;
    logic tvalid;
    logic tready;
    logic tlast;   

    // clocking block for AXI Stream master
    clocking cb_axis_m @(posedge aclk);
      default input #1step output #3ns;
      output tdata;
      output tvalid;
      output tlast;
      input tready;
    endclocking

    // clocking block for AXI Stream slave
    clocking cb_axis_s @(posedge aclk);
      default input #1step output #2ns;
      input tdata;
      input tvalid;
      input tlast;
      output tready;
    endclocking     

    // AXI stream master modport - for testbench only
    modport tb_axis_m_mp(
        clocking cb_axis_mst,
        output tdata,
        output tvalid,
        output tlast,
        input tready
    );

    // AXI stream slave modport - for testbench only
    modport tb_axis_s_mp(
        clocking cb_axis_slv,
        input tdata,
        input tvalid,
        input tlast,
        output tready
    );   
    
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
    
endinterface: axis