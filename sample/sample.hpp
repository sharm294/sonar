#ifndef SAMPLES_H_
#define SAMPLES_H_

#include "ap_int.h"
#include "ap_axi_sdata.h"
#include "hls_stream.h"

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

#define WRITE_WORD(Aword, Adata, Alast, Aaxis)\
    Aword.data = Adata;\
    Aword.last = Alast;\
    Aaxis.write(Aword);

#define READ_WORD(Aword, Adata, Alast, Aaxis)\
    Aaxis.read(Aword);\
    Adata = Aword.data;\
    Alast = Aword.last;

//the arg numbers correspond to the c_args order in axis.py
#define WRITE(interface)\
    WRITE_WORD(axis_word, args[0], args[1], interface)

#define READ(interface)\
    READ_WORD(axis_word, readArgs[0], readArgs[1], interface)

#define VERIFY\
    if(args[0] != readArgs[0] || args[1] != readArgs[1]){\
        valid = false;\
        std::cout << "Mismatch at id: " << id << "\n";\
        std::cout << std::hex << "   Expected: " << readArgs[0] << " " << \
            readArgs[1] << "\n";\
        std::cout << std::hex << "   Received: " << args[0] << " " << \
            args[1] << "\n";\
    }

#endif
