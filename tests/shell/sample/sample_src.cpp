/*******************************************************************************

The MIT License (MIT)

Copyright (c) 2020 Varun Sharma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*******************************************************************************/

#include "sample_src.hpp"

void sample_src(
  volatile uint_3_t *state_out,
  uint_1_t* ack,
  axis_t* axis_output,
  axis_t* axis_input,
  uint_1_t enable
) {
#pragma HLS INTERFACE axis port = axis_input
#pragma HLS INTERFACE axis port = axis_output
#pragma HLS INTERFACE ap_none port = state_out
#pragma HLS INTERFACE s_axilite port = enable bundle = ctrl_bus
#pragma HLS INTERFACE ap_ctrl_none port = return
#pragma HLS INTERFACE ap_none port = ack
#pragma HLS PIPELINE II = 1

  enum state_t { st_header = 0, st_payload, st_output, ack1, ack2 };

  static state_t currentState = st_header;
#pragma HLS reset variable = currentState

  axis_word_t axis_word;
  static uint_64_t payload = 3;
#pragma HLS reset variable = payload

  static uint_1_t ack_wire = 0;
#pragma HLS reset variable = ack_wire

  switch (currentState) {
    case st_header: {
      if (!axis_input->empty() && enable == 1) {
        axis_input->read(axis_word);
        currentState = ack1;
      } else {
        currentState = st_header;
      }
      ack_wire = 0;
      break;
    }
    case ack1: {
      ack_wire = 1;
      currentState = st_payload;
      break;
    }
    case st_payload: {
      if (!axis_input->empty()) {
        axis_input->read(axis_word);
        payload = axis_word.tdata;
        currentState = ack2;
      } else {
        currentState = st_payload;
      }
      ack_wire = 0;
      break;
    }
    case ack2: {
      ack_wire = 1;
      currentState = st_output;
      break;
    }
    case st_output: {
      axis_word.tdata = payload + 1;
      axis_output->write(axis_word);
      currentState = st_header;
      ack_wire = 0;
      break;
    }
  }

  *state_out = currentState;
  *ack = ack_wire;
}
