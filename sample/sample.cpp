#include "sample.hpp"

void sample(
    axis_t &axis_input,
    axis_t &axis_output,
    uint_1_t &ack,
    uint_1_t enable,
    volatile uint_3_t * state_out
){

    #pragma HLS INTERFACE axis port=axis_input
    #pragma HLS INTERFACE axis port=axis_output
    #pragma HLS INTERFACE ap_none port=state_out
    #pragma HLS INTERFACE s_axilite port=enable bundle=ctrl_bus
    #pragma HLS INTERFACE ap_ctrl_none port=return
    #pragma HLS INTERFACE ap_none port=ack
    #pragma HLS PIPELINE II=1    

    enum state_t{st_header = 0, st_payload, st_output, ack1, ack2};

    static state_t currentState = st_header;
    #pragma HLS reset variable=currentState

    axis_word_t axis_word;
    static uint_64_t payload = 3;
    #pragma HLS reset variable=payload
    
    static uint_1_t ack_wire = 0;
    #pragma HLS reset variable=ack_wire

    switch(currentState){
        case st_header:{
            if(!axis_input.empty() && enable == 1){
                axis_input.read(axis_word);
                currentState = ack1;
            }
            else
                currentState = st_header;
            ack_wire = 0;
            break;
        }
        case ack1:{
            ack_wire = 1;
            currentState = st_payload;
            break;
        }
        case st_payload:{
            if(!axis_input.empty()){
                axis_input.read(axis_word);
                payload = axis_word.data;
                currentState = ack2;
            }
            else
                currentState = st_payload;
            ack_wire = 0;
            break;
        }
        case ack2:{
            ack_wire = 1;
            currentState = st_output;
            break;
        }
        case st_output:{
            axis_word.data = payload + 1;
            axis_output.write(axis_word);
            currentState = st_header;
            ack_wire = 0;
            break;
        }
    }

    *state_out = currentState;
    ack = ack_wire;
}
