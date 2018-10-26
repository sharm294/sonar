#ifndef SAMPLES_H_
#define SAMPLES_H_

#include "ap_int.h"
#include "ap_axi_sdata.h"
#include "hls_stream.h"
#include "utilities.hpp"

template<int D>
struct uaxis_l{
    ap_uint<D> data;
    ap_uint<1> last;
};

typedef uaxis_l<64> axis_word_t;
typedef hls::stream<axis_word_t> axis_t;
typedef ap_uint<1> uint_1_t;
typedef ap_uint<3> uint_3_t;
typedef ap_uint<64> uint_64_t;

void sample(
    axis_t &axis_input,
    axis_t &axis_output,
    uint_1_t &ack,
    volatile uint_3_t * state_out
);

#define DECLARE_VARIABLES\
    axis_t axis_input;\
    axis_t axis_output;\
    uint_1_t ack;\
    uint_3_t state_out;\
    axis_word_t axis_word;

#define CALL_TB sample(axis_input, axis_output, ack, &state_out);

#define COMPARE_uaxis_l(x) x

#define WRITE_WORD_L(Aword, Adata, Alast, Aaxis)\
    Aword.data = Adata;\
    Aword.last = Alast;\
    Aaxis.write(Aword);
#define READ_WORD_L(Aword, Adata, Alast, Aaxis)\
    Aaxis.read(Aword);\
    Adata = Aword.data;\
    Alast = Aword.last;
//the arg numbers correspond to the c_args order in axis.py in Sonar
#define WRITE(key, word_type, interface)\
    WHEN(EQUAL(key, uaxis_l))\
        (WRITE_WORD_L(word_type, args[0], args[1], interface))

#define READ(key, word_type, interface)\
    WHEN(EQUAL(key, uaxis_l))\
        (READ_WORD_L(word_type, readArgs[0], readArgs[1], interface))

#define VERIFY(key)\
    if(!strcmp(key,"uaxis_l")){\
        if(args[0] != readArgs[0] || args[1] != readArgs[1]){\
            valid = false;\
            std::cout << "Mismatch at id: " << id << "\n";\
            std::cout << std::hex << "   Expected: " << args[0] << " " << \
                args[1] << "\n";\
            std::cout << std::hex << "   Received: " << readArgs[0] << " " << \
                readArgs[1] << "\n";\
        }\
    }

#define PRINT_INTERFACES std::cout << "Stream statuses:\n"; \
    std::cout << "axis_in: " << axis_input.size() << "\n";\
    std::cout << "axis_out: " << axis_output.size() << "\n";

#define READ_STREAM_INTERFACE(name, key, stream, word_type) \
    while(stream.size() > 0){ \
        WHEN(EQUAL(key, uaxis_l))(\
            READ(key, word_type, stream) \
            std::cout << std::hex << name << " - Data: " << word_type.data << \
            " Last: " << word_type.last << "\n"; \
        )\
    }

#define READ_INTERFACES \
    READ_STREAM_INTERFACE("Input", uaxis_l, axis_input, axis_word)\
    READ_STREAM_INTERFACE("Output", uaxis_l, axis_output, axis_word)

#endif
