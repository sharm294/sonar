#ifndef STREAM_H_
#define STREAM_H_

#include "types.hpp"
#include "ap_axi_sdata.h"
#include "hls_stream.h"

template<int D>
struct uaxis_l{
    ap_uint<D> data;
    ap_uint<1> last;
};

//stream - DATA, USER, ID, DEST bits, in that order
// typedef uaxis_l<32> axis_word_32a_t;
// typedef uaxis_l<72> axis_word_72a_t;

// typedef hls::stream<axis_word_32a_t> axis_32a_t;

#define WRITE_WORD(Aword, Adata, Alast, Aaxis)\
    Aword.data = Adata;\
    Aword.last = Alast;\
    Aaxis.write(Aword);

#define READ_WORD(Aword, Adata, Alast, Aaxis)\
    Aaxis.read(Aword);\
    Adata = Aword.data;\
    Alast = Aword.last;

#endif