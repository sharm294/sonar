#ifndef TYPES_H_
#define TYPES_H_

#include "ap_int.h"

//typedefs

//unsigned int
typedef ap_uint<1> uint_1_t;
typedef ap_uint<2> uint_2_t;
typedef ap_uint<4> uint_4_t;
typedef ap_uint<6> uint_6_t;
typedef ap_uint<7> uint_7_t;
typedef ap_uint<8> uint_8_t;
typedef ap_uint<9> uint_9_t;
typedef ap_uint<12> uint_12_t;
typedef ap_uint<13> uint_13_t;
typedef ap_uint<16> uint_16_t;
typedef ap_uint<22> uint_22_t;
typedef ap_uint<23> uint_23_t;
typedef ap_uint<32> uint_32_t;
typedef ap_uint<64> uint_64_t;
typedef ap_uint<72> uint_72_t;

#define NBITS2(n) ((n&2)?1:0)
#define NBITS4(n) ((n&(0xC))?(2+NBITS2(n>>2)):(NBITS2(n)))
#define NBITS8(n) ((n&0xF0)?(4+NBITS4(n>>4)):(NBITS4(n)))
#define NBITS16(n) ((n&0xFF00)?(8+NBITS8(n>>8)):(NBITS8(n)))
#define NBITS32(n) ((n&0xFFFF0000)?(16+NBITS16(n>>16)):(NBITS16(n)))
#define NBITS64(n) ((n&0xFFFFFFFF0000)?(32+NBITS32(n>>32)):(NBITS32(n)))
#define NBITS(n) (n==0?0:NBITS64(n)+1)

#endif
