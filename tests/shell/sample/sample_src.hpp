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
// #include "utilities.hpp"

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

void sample_src(
  volatile uint_3_t *state_out,
  uint_1_t* ack,
  axis_t* axis_output,
  axis_t* axis_input,
  uint_1_t enable
);

// #define DECLARE_VARIABLES \
//   axis_t axis_input;      \
//   axis_t axis_output;     \
//   uint_1_t ack;           \
//   uint_1_t enable = 1;    \
//   uint_3_t state_out;     \
//   axis_word_t axis_word;

#define CALL_TB sample_src(&state_out, &ack, &axis_output, &axis_input, enable);

// #define COMPARE_simple_flit(x) x

// #define WRITE_WORD_L(Aword, Adata, Alast, Aaxis) \
//   Aword.data = Adata;                            \
//   Aword.last = Alast;                            \
//   Aaxis.write(Aword);
// #define READ_WORD_L(Aword, Adata, Alast, Aaxis) \
//   Aaxis.read(Aword);                            \
//   Adata = Aword.data;                           \
//   Alast = Aword.last;
// // the arg numbers correspond to the c_args order in axis.py in Sonar
// #define WRITE(key, word_type, interface) \
//   WHEN(EQUAL(key, simple_flit))              \
//   (WRITE_WORD_L(word_type, args[0], args[1], interface))

// #define READ(key, word_type, interface) \
//   WHEN(EQUAL(key, simple_flit))             \
//   (READ_WORD_L(word_type, readArgs[0], readArgs[1], interface))

// #define VERIFY(key)                                                         \
//   if (!strcmp(key, "simple_flit")) {                                        \
//     if (args[0] != readArgs[0] || args[1] != readArgs[1]) {                 \
//       valid = false;                                                        \
//       std::cout << "Mismatch at id: " << id << "\n";                        \
//       std::cout << std::hex << "   Expected: " << args[0] << " " << args[1] \
//                 << "\n";                                                    \
//       std::cout << std::hex << "   Received: " << readArgs[0] << " "        \
//                 << readArgs[1] << "\n";                                     \
//     }                                                                       \
//   }

// #define PRINT_INTERFACES                                 \
//   std::cout << "Stream statuses:\n";                     \
//   std::cout << "axis_in: " << axis_input.size() << "\n"; \
//   std::cout << "axis_out: " << axis_output.size() << "\n";

// #define READ_STREAM_INTERFACE(name, key, stream, word_type)   \
//   while (stream.size() > 0) {                                 \
//     WHEN(EQUAL(key, simple_flit))                                 \
//     (READ(key, word_type, stream) std::cout                   \
//          << std::hex << name << " - Data: " << word_type.data \
//          << " Last: " << word_type.last << "\n";)             \
//   }

// #define READ_INTERFACES                                          \
//   READ_STREAM_INTERFACE("Input", simple_flit, axis_input, axis_word) \
//   READ_STREAM_INTERFACE("Output", simple_flit, axis_output, axis_word)
