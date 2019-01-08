// ==============================================================
// RTL generated by Vivado(TM) HLS - High-Level Synthesis from C, C++ and SystemC
// Version: 2017.2
// Copyright (C) 1986-2017 Xilinx, Inc. All Rights Reserved.
// 
// ===========================================================

`timescale 1 ns / 1 ps 

(* CORE_GENERATION_INFO="sample,hls_ip_2017_2,{HLS_INPUT_TYPE=cxx,HLS_INPUT_FLOAT=0,HLS_INPUT_FIXED=1,HLS_INPUT_PART=xcvu095-ffvc1517-2-e,HLS_INPUT_CLOCK=4.000000,HLS_INPUT_ARCH=pipeline,HLS_SYN_CLOCK=2.517000,HLS_SYN_LAT=2,HLS_SYN_TPT=1,HLS_SYN_MEM=0,HLS_SYN_DSP=0,HLS_SYN_FF=452,HLS_SYN_LUT=284}" *)

module sample (
        ap_clk,
        ap_rst_n,
        axis_input_TDATA,
        axis_input_TVALID,
        axis_input_TREADY,
        axis_input_TLAST,
        axis_output_TDATA,
        axis_output_TVALID,
        axis_output_TREADY,
        axis_output_TLAST,
        ack_V,
        state_out_V,
        s_axi_ctrl_bus_AWVALID,
        s_axi_ctrl_bus_AWREADY,
        s_axi_ctrl_bus_AWADDR,
        s_axi_ctrl_bus_WVALID,
        s_axi_ctrl_bus_WREADY,
        s_axi_ctrl_bus_WDATA,
        s_axi_ctrl_bus_WSTRB,
        s_axi_ctrl_bus_ARVALID,
        s_axi_ctrl_bus_ARREADY,
        s_axi_ctrl_bus_ARADDR,
        s_axi_ctrl_bus_RVALID,
        s_axi_ctrl_bus_RREADY,
        s_axi_ctrl_bus_RDATA,
        s_axi_ctrl_bus_RRESP,
        s_axi_ctrl_bus_BVALID,
        s_axi_ctrl_bus_BREADY,
        s_axi_ctrl_bus_BRESP
);

parameter    ap_ST_fsm_pp0_stage0 = 1'd1;
parameter    C_S_AXI_CTRL_BUS_DATA_WIDTH = 32;
parameter    C_S_AXI_CTRL_BUS_ADDR_WIDTH = 5;
parameter    C_S_AXI_DATA_WIDTH = 32;

parameter C_S_AXI_CTRL_BUS_WSTRB_WIDTH = (32 / 8);
parameter C_S_AXI_WSTRB_WIDTH = (32 / 8);

input   ap_clk;
input   ap_rst_n;
input  [63:0] axis_input_TDATA;
input   axis_input_TVALID;
output   axis_input_TREADY;
input  [0:0] axis_input_TLAST;
output  [63:0] axis_output_TDATA;
output   axis_output_TVALID;
input   axis_output_TREADY;
output  [0:0] axis_output_TLAST;
output  [0:0] ack_V;
output  [2:0] state_out_V;
input   s_axi_ctrl_bus_AWVALID;
output   s_axi_ctrl_bus_AWREADY;
input  [C_S_AXI_CTRL_BUS_ADDR_WIDTH - 1:0] s_axi_ctrl_bus_AWADDR;
input   s_axi_ctrl_bus_WVALID;
output   s_axi_ctrl_bus_WREADY;
input  [C_S_AXI_CTRL_BUS_DATA_WIDTH - 1:0] s_axi_ctrl_bus_WDATA;
input  [C_S_AXI_CTRL_BUS_WSTRB_WIDTH - 1:0] s_axi_ctrl_bus_WSTRB;
input   s_axi_ctrl_bus_ARVALID;
output   s_axi_ctrl_bus_ARREADY;
input  [C_S_AXI_CTRL_BUS_ADDR_WIDTH - 1:0] s_axi_ctrl_bus_ARADDR;
output   s_axi_ctrl_bus_RVALID;
input   s_axi_ctrl_bus_RREADY;
output  [C_S_AXI_CTRL_BUS_DATA_WIDTH - 1:0] s_axi_ctrl_bus_RDATA;
output  [1:0] s_axi_ctrl_bus_RRESP;
output   s_axi_ctrl_bus_BVALID;
input   s_axi_ctrl_bus_BREADY;
output  [1:0] s_axi_ctrl_bus_BRESP;

reg axis_input_TREADY;

reg    ap_rst_n_inv;
reg   [63:0] axis_output_V_data_V_1_data_out;
reg    axis_output_V_data_V_1_vld_in;
wire    axis_output_V_data_V_1_vld_out;
wire    axis_output_V_data_V_1_ack_in;
wire    axis_output_V_data_V_1_ack_out;
reg   [63:0] axis_output_V_data_V_1_payload_A;
reg   [63:0] axis_output_V_data_V_1_payload_B;
reg    axis_output_V_data_V_1_sel_rd;
reg    axis_output_V_data_V_1_sel_wr;
wire    axis_output_V_data_V_1_sel;
wire    axis_output_V_data_V_1_load_A;
wire    axis_output_V_data_V_1_load_B;
reg   [1:0] axis_output_V_data_V_1_state;
wire    axis_output_V_data_V_1_state_cmp_full;
wire   [0:0] axis_output_V_last_V_1_data_out;
reg    axis_output_V_last_V_1_vld_in;
wire    axis_output_V_last_V_1_vld_out;
wire    axis_output_V_last_V_1_ack_in;
wire    axis_output_V_last_V_1_ack_out;
reg    axis_output_V_last_V_1_sel_rd;
wire    axis_output_V_last_V_1_sel;
reg   [1:0] axis_output_V_last_V_1_state;
wire   [0:0] enable_V;
reg   [2:0] currentState;
reg   [0:0] ack_wire_V;
reg   [63:0] payload_V;
reg    axis_input_TDATA_blk_n;
(* fsm_encoding = "none" *) reg   [0:0] ap_CS_fsm;
wire    ap_CS_fsm_pp0_stage0;
wire    ap_block_pp0_stage0_flag00000000;
wire   [2:0] currentState_load_load_fu_192_p1;
wire   [0:0] brmerge_demorgan_fu_230_p2;
wire   [0:0] grp_nbreadreq_fu_86_p4;
reg    axis_output_TDATA_blk_n;
reg    ap_enable_reg_pp0_iter1;
reg   [2:0] currentState_load_reg_258;
reg    ap_enable_reg_pp0_iter2;
reg   [2:0] ap_reg_pp0_iter1_currentState_load_reg_258;
reg   [2:0] tmp_7_reg_153;
reg    ap_predicate_op13_read_state1;
reg    ap_predicate_op25_read_state1;
reg    ap_block_state1_pp0_stage0_iter0;
wire    ap_block_state2_pp0_stage0_iter1;
reg    ap_block_state2_io;
reg    ap_block_state3_pp0_stage0_iter2;
reg    ap_block_state3_io;
reg    ap_block_pp0_stage0_flag00011001;
wire   [63:0] tmp_data_V_fu_246_p2;
reg    ap_block_pp0_stage0_flag00011011;
wire   [2:0] ap_phi_precharge_reg_pp0_iter0_storemerge_reg_129;
reg   [2:0] storemerge_phi_fu_132_p4;
wire   [2:0] ap_phi_precharge_reg_pp0_iter0_storemerge1_reg_141;
reg   [2:0] storemerge1_phi_fu_144_p4;
wire   [2:0] ap_phi_precharge_reg_pp0_iter0_tmp_7_reg_153;
reg   [2:0] ap_phi_precharge_reg_pp0_iter1_tmp_7_reg_153;
reg    ap_block_pp0_stage0_flag00001001;
reg   [0:0] ap_NS_fsm;
wire    ap_reset_idle_pp0;
reg    ap_idle_pp0;
wire    ap_enable_pp0;
reg    ap_condition_302;
reg    ap_condition_269;
reg    ap_condition_401;
reg    ap_condition_404;

// power-on initialization
initial begin
#0 axis_output_V_data_V_1_sel_rd = 1'b0;
#0 axis_output_V_data_V_1_sel_wr = 1'b0;
#0 axis_output_V_data_V_1_state = 2'd0;
#0 axis_output_V_last_V_1_sel_rd = 1'b0;
#0 axis_output_V_last_V_1_state = 2'd0;
#0 currentState = 3'd0;
#0 ack_wire_V = 1'd0;
#0 payload_V = 64'd3;
#0 ap_CS_fsm = 1'd1;
#0 ap_enable_reg_pp0_iter1 = 1'b0;
#0 ap_enable_reg_pp0_iter2 = 1'b0;
end

sample_ctrl_bus_s_axi #(
    .C_S_AXI_ADDR_WIDTH( C_S_AXI_CTRL_BUS_ADDR_WIDTH ),
    .C_S_AXI_DATA_WIDTH( C_S_AXI_CTRL_BUS_DATA_WIDTH ))
sample_ctrl_bus_s_axi_U(
    .AWVALID(s_axi_ctrl_bus_AWVALID),
    .AWREADY(s_axi_ctrl_bus_AWREADY),
    .AWADDR(s_axi_ctrl_bus_AWADDR),
    .WVALID(s_axi_ctrl_bus_WVALID),
    .WREADY(s_axi_ctrl_bus_WREADY),
    .WDATA(s_axi_ctrl_bus_WDATA),
    .WSTRB(s_axi_ctrl_bus_WSTRB),
    .ARVALID(s_axi_ctrl_bus_ARVALID),
    .ARREADY(s_axi_ctrl_bus_ARREADY),
    .ARADDR(s_axi_ctrl_bus_ARADDR),
    .RVALID(s_axi_ctrl_bus_RVALID),
    .RREADY(s_axi_ctrl_bus_RREADY),
    .RDATA(s_axi_ctrl_bus_RDATA),
    .RRESP(s_axi_ctrl_bus_RRESP),
    .BVALID(s_axi_ctrl_bus_BVALID),
    .BREADY(s_axi_ctrl_bus_BREADY),
    .BRESP(s_axi_ctrl_bus_BRESP),
    .ACLK(ap_clk),
    .ARESET(ap_rst_n_inv),
    .ACLK_EN(1'b1),
    .enable_V(enable_V)
);

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        ack_wire_V <= 1'd0;
    end else begin
        if ((((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == ap_enable_reg_pp0_iter1) & (ap_block_pp0_stage0_flag00011001 == 1'b0) & (currentState_load_reg_258 == 3'd4)) | ((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == ap_enable_reg_pp0_iter1) & (ap_block_pp0_stage0_flag00011001 == 1'b0) & (currentState_load_reg_258 == 3'd3)))) begin
            ack_wire_V <= 1'd1;
        end else if ((((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == ap_enable_reg_pp0_iter1) & (currentState_load_reg_258 == 3'd2) & (ap_block_pp0_stage0_flag00011001 == 1'b0)) | ((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == ap_enable_reg_pp0_iter1) & (ap_block_pp0_stage0_flag00011001 == 1'b0) & (3'd1 == currentState_load_reg_258)) | ((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == ap_enable_reg_pp0_iter1) & (ap_block_pp0_stage0_flag00011001 == 1'b0) & (3'd0 == currentState_load_reg_258)))) begin
            ack_wire_V <= 1'd0;
        end
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        ap_CS_fsm <= ap_ST_fsm_pp0_stage0;
    end else begin
        ap_CS_fsm <= ap_NS_fsm;
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        ap_enable_reg_pp0_iter1 <= 1'b0;
    end else begin
        if ((ap_block_pp0_stage0_flag00011011 == 1'b0)) begin
            ap_enable_reg_pp0_iter1 <= 1'b1;
        end
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        ap_enable_reg_pp0_iter2 <= 1'b0;
    end else begin
        if ((ap_block_pp0_stage0_flag00011011 == 1'b0)) begin
            ap_enable_reg_pp0_iter2 <= ap_enable_reg_pp0_iter1;
        end
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        axis_output_V_data_V_1_sel_rd <= 1'b0;
    end else begin
        if (((1'b1 == axis_output_V_data_V_1_ack_out) & (1'b1 == axis_output_V_data_V_1_vld_out))) begin
            axis_output_V_data_V_1_sel_rd <= ~axis_output_V_data_V_1_sel_rd;
        end
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        axis_output_V_data_V_1_sel_wr <= 1'b0;
    end else begin
        if (((1'b1 == axis_output_V_data_V_1_vld_in) & (1'b1 == axis_output_V_data_V_1_ack_in))) begin
            axis_output_V_data_V_1_sel_wr <= ~axis_output_V_data_V_1_sel_wr;
        end
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        axis_output_V_data_V_1_state <= 2'd0;
    end else begin
        if ((((1'b0 == axis_output_V_data_V_1_vld_in) & (1'b1 == axis_output_V_data_V_1_ack_out) & (axis_output_V_data_V_1_state == 2'd3)) | ((1'b0 == axis_output_V_data_V_1_vld_in) & (axis_output_V_data_V_1_state == 2'd2)))) begin
            axis_output_V_data_V_1_state <= 2'd2;
        end else if ((((1'b1 == axis_output_V_data_V_1_vld_in) & (1'b0 == axis_output_V_data_V_1_ack_out) & (axis_output_V_data_V_1_state == 2'd3)) | ((1'b0 == axis_output_V_data_V_1_ack_out) & (axis_output_V_data_V_1_state == 2'd1)))) begin
            axis_output_V_data_V_1_state <= 2'd1;
        end else if ((((1'b1 == axis_output_V_data_V_1_vld_in) & (axis_output_V_data_V_1_state == 2'd2)) | ((1'b1 == axis_output_V_data_V_1_ack_out) & (axis_output_V_data_V_1_state == 2'd1)) | ((axis_output_V_data_V_1_state == 2'd3) & ~((1'b1 == axis_output_V_data_V_1_vld_in) & (1'b0 == axis_output_V_data_V_1_ack_out)) & ~((1'b0 == axis_output_V_data_V_1_vld_in) & (1'b1 == axis_output_V_data_V_1_ack_out))))) begin
            axis_output_V_data_V_1_state <= 2'd3;
        end else begin
            axis_output_V_data_V_1_state <= 2'd2;
        end
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        axis_output_V_last_V_1_sel_rd <= 1'b0;
    end else begin
        if (((1'b1 == axis_output_V_last_V_1_ack_out) & (1'b1 == axis_output_V_last_V_1_vld_out))) begin
            axis_output_V_last_V_1_sel_rd <= ~axis_output_V_last_V_1_sel_rd;
        end
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        axis_output_V_last_V_1_state <= 2'd0;
    end else begin
        if ((((1'b0 == axis_output_V_last_V_1_vld_in) & (1'b1 == axis_output_V_last_V_1_ack_out) & (2'd3 == axis_output_V_last_V_1_state)) | ((1'b0 == axis_output_V_last_V_1_vld_in) & (2'd2 == axis_output_V_last_V_1_state)))) begin
            axis_output_V_last_V_1_state <= 2'd2;
        end else if ((((1'b1 == axis_output_V_last_V_1_vld_in) & (1'b0 == axis_output_V_last_V_1_ack_out) & (2'd3 == axis_output_V_last_V_1_state)) | ((1'b0 == axis_output_V_last_V_1_ack_out) & (2'd1 == axis_output_V_last_V_1_state)))) begin
            axis_output_V_last_V_1_state <= 2'd1;
        end else if ((((1'b1 == axis_output_V_last_V_1_vld_in) & (2'd2 == axis_output_V_last_V_1_state)) | ((1'b1 == axis_output_V_last_V_1_ack_out) & (2'd1 == axis_output_V_last_V_1_state)) | ((2'd3 == axis_output_V_last_V_1_state) & ~((1'b1 == axis_output_V_last_V_1_vld_in) & (1'b0 == axis_output_V_last_V_1_ack_out)) & ~((1'b0 == axis_output_V_last_V_1_vld_in) & (1'b1 == axis_output_V_last_V_1_ack_out))))) begin
            axis_output_V_last_V_1_state <= 2'd3;
        end else begin
            axis_output_V_last_V_1_state <= 2'd2;
        end
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        currentState <= 3'd0;
    end else begin
        if ((ap_condition_269 == 1'b1)) begin
            if ((3'd0 == currentState)) begin
                currentState <= storemerge1_phi_fu_144_p4;
            end else if ((currentState_load_load_fu_192_p1 == 3'd3)) begin
                currentState <= 3'd1;
            end else if ((currentState == 3'd1)) begin
                currentState <= storemerge_phi_fu_132_p4;
            end else if ((currentState_load_load_fu_192_p1 == 3'd4)) begin
                currentState <= 3'd2;
            end else if ((currentState_load_load_fu_192_p1 == 3'd2)) begin
                currentState <= 3'd0;
            end
        end
    end
end

always @ (posedge ap_clk) begin
    if (ap_rst_n_inv == 1'b1) begin
        payload_V <= 64'd3;
    end else begin
        if (((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == 1'b1) & (1'b1 == ap_predicate_op13_read_state1) & (ap_block_pp0_stage0_flag00011001 == 1'b0))) begin
            payload_V <= axis_input_TDATA;
        end
    end
end

always @ (posedge ap_clk) begin
    if ((ap_condition_269 == 1'b1)) begin
        if ((3'd0 == currentState)) begin
            ap_phi_precharge_reg_pp0_iter1_tmp_7_reg_153 <= storemerge1_phi_fu_144_p4;
        end else if ((currentState == 3'd1)) begin
            ap_phi_precharge_reg_pp0_iter1_tmp_7_reg_153 <= storemerge_phi_fu_132_p4;
        end else if ((ap_condition_302 == 1'b1)) begin
            ap_phi_precharge_reg_pp0_iter1_tmp_7_reg_153 <= currentState;
        end else if ((currentState_load_load_fu_192_p1 == 3'd3)) begin
            ap_phi_precharge_reg_pp0_iter1_tmp_7_reg_153 <= 3'd1;
        end else if ((currentState_load_load_fu_192_p1 == 3'd4)) begin
            ap_phi_precharge_reg_pp0_iter1_tmp_7_reg_153 <= 3'd2;
        end else if ((currentState_load_load_fu_192_p1 == 3'd2)) begin
            ap_phi_precharge_reg_pp0_iter1_tmp_7_reg_153 <= 3'd0;
        end else if ((1'b1 == 1'b1)) begin
            ap_phi_precharge_reg_pp0_iter1_tmp_7_reg_153 <= ap_phi_precharge_reg_pp0_iter0_tmp_7_reg_153;
        end
    end
end

always @ (posedge ap_clk) begin
    if (((1'b1 == ap_CS_fsm_pp0_stage0) & (ap_block_pp0_stage0_flag00011001 == 1'b0))) begin
        ap_reg_pp0_iter1_currentState_load_reg_258 <= currentState_load_reg_258;
        currentState_load_reg_258 <= currentState;
    end
end

always @ (posedge ap_clk) begin
    if ((1'b1 == axis_output_V_data_V_1_load_A)) begin
        axis_output_V_data_V_1_payload_A <= tmp_data_V_fu_246_p2;
    end
end

always @ (posedge ap_clk) begin
    if ((1'b1 == axis_output_V_data_V_1_load_B)) begin
        axis_output_V_data_V_1_payload_B <= tmp_data_V_fu_246_p2;
    end
end

always @ (posedge ap_clk) begin
    if (((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == ap_enable_reg_pp0_iter1) & (ap_block_pp0_stage0_flag00011001 == 1'b0))) begin
        tmp_7_reg_153 <= ap_phi_precharge_reg_pp0_iter1_tmp_7_reg_153;
    end
end

always @ (*) begin
    if (((1'b0 == 1'b1) & (1'b0 == ap_enable_reg_pp0_iter1) & (1'b0 == ap_enable_reg_pp0_iter2))) begin
        ap_idle_pp0 = 1'b1;
    end else begin
        ap_idle_pp0 = 1'b0;
    end
end

assign ap_reset_idle_pp0 = 1'b0;

always @ (*) begin
    if ((((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == 1'b1) & (ap_block_pp0_stage0_flag00000000 == 1'b0) & (3'd0 == currentState) & (1'd1 == brmerge_demorgan_fu_230_p2)) | ((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == 1'b1) & (ap_block_pp0_stage0_flag00000000 == 1'b0) & (currentState == 3'd1) & (1'd1 == grp_nbreadreq_fu_86_p4)))) begin
        axis_input_TDATA_blk_n = axis_input_TVALID;
    end else begin
        axis_input_TDATA_blk_n = 1'b1;
    end
end

always @ (*) begin
    if ((((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == 1'b1) & (1'b1 == ap_predicate_op13_read_state1) & (ap_block_pp0_stage0_flag00011001 == 1'b0)) | ((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == 1'b1) & (1'b1 == ap_predicate_op25_read_state1) & (ap_block_pp0_stage0_flag00011001 == 1'b0)))) begin
        axis_input_TREADY = 1'b1;
    end else begin
        axis_input_TREADY = 1'b0;
    end
end

always @ (*) begin
    if ((((1'b1 == ap_CS_fsm_pp0_stage0) & (ap_block_pp0_stage0_flag00000000 == 1'b0) & (1'b1 == ap_enable_reg_pp0_iter1) & (currentState_load_reg_258 == 3'd2)) | ((ap_block_pp0_stage0_flag00000000 == 1'b0) & (1'b1 == ap_enable_reg_pp0_iter2) & (3'd2 == ap_reg_pp0_iter1_currentState_load_reg_258)))) begin
        axis_output_TDATA_blk_n = axis_output_V_data_V_1_state[1'd1];
    end else begin
        axis_output_TDATA_blk_n = 1'b1;
    end
end

always @ (*) begin
    if ((1'b1 == axis_output_V_data_V_1_sel)) begin
        axis_output_V_data_V_1_data_out = axis_output_V_data_V_1_payload_B;
    end else begin
        axis_output_V_data_V_1_data_out = axis_output_V_data_V_1_payload_A;
    end
end

always @ (*) begin
    if (((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == ap_enable_reg_pp0_iter1) & (currentState_load_reg_258 == 3'd2) & (ap_block_pp0_stage0_flag00011001 == 1'b0))) begin
        axis_output_V_data_V_1_vld_in = 1'b1;
    end else begin
        axis_output_V_data_V_1_vld_in = 1'b0;
    end
end

always @ (*) begin
    if (((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == ap_enable_reg_pp0_iter1) & (currentState_load_reg_258 == 3'd2) & (ap_block_pp0_stage0_flag00011001 == 1'b0))) begin
        axis_output_V_last_V_1_vld_in = 1'b1;
    end else begin
        axis_output_V_last_V_1_vld_in = 1'b0;
    end
end

always @ (*) begin
    if ((ap_condition_401 == 1'b1)) begin
        if ((1'd0 == brmerge_demorgan_fu_230_p2)) begin
            storemerge1_phi_fu_144_p4 = 3'd0;
        end else if ((1'd1 == brmerge_demorgan_fu_230_p2)) begin
            storemerge1_phi_fu_144_p4 = 3'd3;
        end else begin
            storemerge1_phi_fu_144_p4 = ap_phi_precharge_reg_pp0_iter0_storemerge1_reg_141;
        end
    end else begin
        storemerge1_phi_fu_144_p4 = ap_phi_precharge_reg_pp0_iter0_storemerge1_reg_141;
    end
end

always @ (*) begin
    if ((ap_condition_404 == 1'b1)) begin
        if ((1'd0 == grp_nbreadreq_fu_86_p4)) begin
            storemerge_phi_fu_132_p4 = 3'd1;
        end else if ((1'd1 == grp_nbreadreq_fu_86_p4)) begin
            storemerge_phi_fu_132_p4 = 3'd4;
        end else begin
            storemerge_phi_fu_132_p4 = ap_phi_precharge_reg_pp0_iter0_storemerge_reg_129;
        end
    end else begin
        storemerge_phi_fu_132_p4 = ap_phi_precharge_reg_pp0_iter0_storemerge_reg_129;
    end
end

always @ (*) begin
    case (ap_CS_fsm)
        ap_ST_fsm_pp0_stage0 : begin
            ap_NS_fsm = ap_ST_fsm_pp0_stage0;
        end
        default : begin
            ap_NS_fsm = 'bx;
        end
    endcase
end

assign ack_V = ack_wire_V;

assign ap_CS_fsm_pp0_stage0 = ap_CS_fsm[32'd0];

assign ap_block_pp0_stage0_flag00000000 = ~(1'b1 == 1'b1);

always @ (*) begin
    ap_block_pp0_stage0_flag00001001 = (((1'b1 == 1'b1) & (((1'b0 == axis_input_TVALID) & (1'b1 == ap_predicate_op13_read_state1)) | ((1'b0 == axis_input_TVALID) & (1'b1 == ap_predicate_op25_read_state1)))) | ((1'b1 == ap_enable_reg_pp0_iter2) & ((1'b0 == axis_output_V_data_V_1_ack_in) | (1'b0 == axis_output_V_last_V_1_ack_in))));
end

always @ (*) begin
    ap_block_pp0_stage0_flag00011001 = (((1'b1 == 1'b1) & (((1'b0 == axis_input_TVALID) & (1'b1 == ap_predicate_op13_read_state1)) | ((1'b0 == axis_input_TVALID) & (1'b1 == ap_predicate_op25_read_state1)))) | ((1'b1 == ap_enable_reg_pp0_iter1) & (1'b1 == ap_block_state2_io)) | ((1'b1 == ap_enable_reg_pp0_iter2) & ((1'b0 == axis_output_V_data_V_1_ack_in) | (1'b0 == axis_output_V_last_V_1_ack_in) | (1'b1 == ap_block_state3_io))));
end

always @ (*) begin
    ap_block_pp0_stage0_flag00011011 = (((1'b1 == 1'b1) & (((1'b0 == axis_input_TVALID) & (1'b1 == ap_predicate_op13_read_state1)) | ((1'b0 == axis_input_TVALID) & (1'b1 == ap_predicate_op25_read_state1)))) | ((1'b1 == ap_enable_reg_pp0_iter1) & (1'b1 == ap_block_state2_io)) | ((1'b1 == ap_enable_reg_pp0_iter2) & ((1'b0 == axis_output_V_data_V_1_ack_in) | (1'b0 == axis_output_V_last_V_1_ack_in) | (1'b1 == ap_block_state3_io))));
end

always @ (*) begin
    ap_block_state1_pp0_stage0_iter0 = (((1'b0 == axis_input_TVALID) & (1'b1 == ap_predicate_op13_read_state1)) | ((1'b0 == axis_input_TVALID) & (1'b1 == ap_predicate_op25_read_state1)));
end

always @ (*) begin
    ap_block_state2_io = ((currentState_load_reg_258 == 3'd2) & (1'b0 == axis_output_V_data_V_1_ack_in));
end

assign ap_block_state2_pp0_stage0_iter1 = ~(1'b1 == 1'b1);

always @ (*) begin
    ap_block_state3_io = ((3'd2 == ap_reg_pp0_iter1_currentState_load_reg_258) & (1'b0 == axis_output_V_data_V_1_ack_in));
end

always @ (*) begin
    ap_block_state3_pp0_stage0_iter2 = ((1'b0 == axis_output_V_data_V_1_ack_in) | (1'b0 == axis_output_V_last_V_1_ack_in));
end

always @ (*) begin
    ap_condition_269 = ((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == 1'b1) & (ap_block_pp0_stage0_flag00011001 == 1'b0));
end

always @ (*) begin
    ap_condition_302 = (~(currentState_load_load_fu_192_p1 == 3'd2) & ~(currentState_load_load_fu_192_p1 == 3'd4) & ~(currentState == 3'd1) & ~(currentState_load_load_fu_192_p1 == 3'd3) & ~(3'd0 == currentState));
end

always @ (*) begin
    ap_condition_401 = ((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == 1'b1) & (ap_block_pp0_stage0_flag00000000 == 1'b0) & (3'd0 == currentState));
end

always @ (*) begin
    ap_condition_404 = ((1'b1 == ap_CS_fsm_pp0_stage0) & (1'b1 == 1'b1) & (ap_block_pp0_stage0_flag00000000 == 1'b0) & (currentState == 3'd1));
end

assign ap_enable_pp0 = (ap_idle_pp0 ^ 1'b1);

assign ap_phi_precharge_reg_pp0_iter0_storemerge1_reg_141 = 'bx;

assign ap_phi_precharge_reg_pp0_iter0_storemerge_reg_129 = 'bx;

assign ap_phi_precharge_reg_pp0_iter0_tmp_7_reg_153 = 'bx;

always @ (*) begin
    ap_predicate_op13_read_state1 = ((currentState == 3'd1) & (1'd1 == grp_nbreadreq_fu_86_p4));
end

always @ (*) begin
    ap_predicate_op25_read_state1 = ((3'd0 == currentState) & (1'd1 == brmerge_demorgan_fu_230_p2));
end

always @ (*) begin
    ap_rst_n_inv = ~ap_rst_n;
end

assign axis_output_TDATA = axis_output_V_data_V_1_data_out;

assign axis_output_TLAST = axis_output_V_last_V_1_data_out;

assign axis_output_TVALID = axis_output_V_last_V_1_state[1'd0];

assign axis_output_V_data_V_1_ack_in = axis_output_V_data_V_1_state[1'd1];

assign axis_output_V_data_V_1_ack_out = axis_output_TREADY;

assign axis_output_V_data_V_1_load_A = (axis_output_V_data_V_1_state_cmp_full & ~axis_output_V_data_V_1_sel_wr);

assign axis_output_V_data_V_1_load_B = (axis_output_V_data_V_1_sel_wr & axis_output_V_data_V_1_state_cmp_full);

assign axis_output_V_data_V_1_sel = axis_output_V_data_V_1_sel_rd;

assign axis_output_V_data_V_1_state_cmp_full = ((axis_output_V_data_V_1_state != 2'd1) ? 1'b1 : 1'b0);

assign axis_output_V_data_V_1_vld_out = axis_output_V_data_V_1_state[1'd0];

assign axis_output_V_last_V_1_ack_in = axis_output_V_last_V_1_state[1'd1];

assign axis_output_V_last_V_1_ack_out = axis_output_TREADY;

assign axis_output_V_last_V_1_data_out = 1'd0;

assign axis_output_V_last_V_1_sel = axis_output_V_last_V_1_sel_rd;

assign axis_output_V_last_V_1_vld_out = axis_output_V_last_V_1_state[1'd0];

assign brmerge_demorgan_fu_230_p2 = (grp_nbreadreq_fu_86_p4 & enable_V);

assign currentState_load_load_fu_192_p1 = currentState;

assign grp_nbreadreq_fu_86_p4 = axis_input_TVALID;

assign state_out_V = tmp_7_reg_153;

assign tmp_data_V_fu_246_p2 = (payload_V + 64'd1);

endmodule //sample

// ==============================================================
// File generated by Vivado(TM) HLS - High-Level Synthesis from C, C++ and SystemC
// Version: 2017.2
// Copyright (C) 1986-2017 Xilinx, Inc. All Rights Reserved.
// 
// ==============================================================

module sample_ctrl_bus_s_axi
#(parameter
    C_S_AXI_ADDR_WIDTH = 5,
    C_S_AXI_DATA_WIDTH = 32
)(
    // axi4 lite slave signals
    input  wire                          ACLK,
    input  wire                          ARESET,
    input  wire                          ACLK_EN,
    input  wire [C_S_AXI_ADDR_WIDTH-1:0] AWADDR,
    input  wire                          AWVALID,
    output wire                          AWREADY,
    input  wire [C_S_AXI_DATA_WIDTH-1:0] WDATA,
    input  wire [C_S_AXI_DATA_WIDTH/8-1:0] WSTRB,
    input  wire                          WVALID,
    output wire                          WREADY,
    output wire [1:0]                    BRESP,
    output wire                          BVALID,
    input  wire                          BREADY,
    input  wire [C_S_AXI_ADDR_WIDTH-1:0] ARADDR,
    input  wire                          ARVALID,
    output wire                          ARREADY,
    output wire [C_S_AXI_DATA_WIDTH-1:0] RDATA,
    output wire [1:0]                    RRESP,
    output wire                          RVALID,
    input  wire                          RREADY,
    // user signals
    output wire [0:0]                    enable_V
);
//------------------------Address Info-------------------
// 0x00 : reserved
// 0x04 : reserved
// 0x08 : reserved
// 0x0c : reserved
// 0x10 : Data signal of enable_V
//        bit 0  - enable_V[0] (Read/Write)
//        others - reserved
// 0x14 : reserved
// (SC = Self Clear, COR = Clear on Read, TOW = Toggle on Write, COH = Clear on Handshake)

//------------------------Parameter----------------------
localparam
    ADDR_ENABLE_V_DATA_0 = 5'h10,
    ADDR_ENABLE_V_CTRL   = 5'h14,
    WRIDLE               = 2'd0,
    WRDATA               = 2'd1,
    WRRESP               = 2'd2,
    WRRESET              = 2'd3,
    RDIDLE               = 2'd0,
    RDDATA               = 2'd1,
    RDRESET              = 2'd2,
    ADDR_BITS         = 5;

//------------------------Local signal-------------------
    reg  [1:0]                    wstate = WRRESET;
    reg  [1:0]                    wnext;
    reg  [ADDR_BITS-1:0]          waddr;
    wire [31:0]                   wmask;
    wire                          aw_hs;
    wire                          w_hs;
    reg  [1:0]                    rstate = RDRESET;
    reg  [1:0]                    rnext;
    reg  [31:0]                   rdata;
    wire                          ar_hs;
    wire [ADDR_BITS-1:0]          raddr;
    // internal registers
    reg  [0:0]                    int_enable_V = 'b0;

//------------------------Instantiation------------------

//------------------------AXI write fsm------------------
assign AWREADY = (wstate == WRIDLE);
assign WREADY  = (wstate == WRDATA);
assign BRESP   = 2'b00;  // OKAY
assign BVALID  = (wstate == WRRESP);
assign wmask   = { {8{WSTRB[3]}}, {8{WSTRB[2]}}, {8{WSTRB[1]}}, {8{WSTRB[0]}} };
assign aw_hs   = AWVALID & AWREADY;
assign w_hs    = WVALID & WREADY;

// wstate
always @(posedge ACLK) begin
    if (ARESET)
        wstate <= WRRESET;
    else if (ACLK_EN)
        wstate <= wnext;
end

// wnext
always @(*) begin
    case (wstate)
        WRIDLE:
            if (AWVALID)
                wnext = WRDATA;
            else
                wnext = WRIDLE;
        WRDATA:
            if (WVALID)
                wnext = WRRESP;
            else
                wnext = WRDATA;
        WRRESP:
            if (BREADY)
                wnext = WRIDLE;
            else
                wnext = WRRESP;
        default:
            wnext = WRIDLE;
    endcase
end

// waddr
always @(posedge ACLK) begin
    if (ACLK_EN) begin
        if (aw_hs)
            waddr <= AWADDR[ADDR_BITS-1:0];
    end
end

//------------------------AXI read fsm-------------------
assign ARREADY = (rstate == RDIDLE);
assign RDATA   = rdata;
assign RRESP   = 2'b00;  // OKAY
assign RVALID  = (rstate == RDDATA);
assign ar_hs   = ARVALID & ARREADY;
assign raddr   = ARADDR[ADDR_BITS-1:0];

// rstate
always @(posedge ACLK) begin
    if (ARESET)
        rstate <= RDRESET;
    else if (ACLK_EN)
        rstate <= rnext;
end

// rnext
always @(*) begin
    case (rstate)
        RDIDLE:
            if (ARVALID)
                rnext = RDDATA;
            else
                rnext = RDIDLE;
        RDDATA:
            if (RREADY & RVALID)
                rnext = RDIDLE;
            else
                rnext = RDDATA;
        default:
            rnext = RDIDLE;
    endcase
end

// rdata
always @(posedge ACLK) begin
    if (ACLK_EN) begin
        if (ar_hs) begin
            rdata <= 1'b0;
            case (raddr)
                ADDR_ENABLE_V_DATA_0: begin
                    rdata <= int_enable_V[0:0];
                end
            endcase
        end
    end
end


//------------------------Register logic-----------------
assign enable_V = int_enable_V;
// int_enable_V[0:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_enable_V[0:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_ENABLE_V_DATA_0)
            int_enable_V[0:0] <= (WDATA[31:0] & wmask) | (int_enable_V[0:0] & ~wmask);
    end
end


//------------------------Memory logic-------------------

endmodule
