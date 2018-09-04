#include "stream.hpp"

typedef uaxis_l<64> axis_word_t;
typedef hls::stream<axis_word_t> axis_t;

void sample(
    axis_t &axis_input,
    axis_t &axis_output,
    uint_1_t &ack,
    volatile uint_3_t * state_out
);