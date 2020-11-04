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

#pragma once

#include "ap_axi_sdata.h"
#include "ap_int.h"
#include "hls_stream.h"

template <int D>
struct simple_flit {
    ap_uint<D> tdata;
    ap_uint<1> tlast;
};

typedef simple_flit<64> axis_word_t;
typedef hls::stream<axis_word_t> axis_t;
typedef ap_uint<1> uint_1_t;
typedef ap_uint<3> uint_3_t;
typedef ap_uint<64> uint_64_t;

void hello_world(
    volatile uint_3_t *state_out,
    uint_1_t* ack,
    axis_t* axis_output,
    axis_t* axis_input,
    uint_1_t enable
);

#define CALL_TB \
    hello_world(&state_out, &ack, &axis_output, &axis_input, enable);
